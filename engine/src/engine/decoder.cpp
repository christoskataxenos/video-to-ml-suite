#include "decoder.hpp"
#include <stdexcept>
#include <cmath>
#include <thread>

Decoder::Decoder(const std::string& filepath)
{
    if (avformat_open_input(&m_fmt_ctx, filepath.c_str(), NULL, NULL) < 0)
        throw std::runtime_error("Could not open video file");

    if (avformat_find_stream_info(m_fmt_ctx, NULL) < 0)
        throw std::runtime_error("Could not find stream info");

    for (unsigned int i = 0; i < m_fmt_ctx->nb_streams; i++)
    {
        if (m_fmt_ctx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO)
        {
            m_video_idx = i;
            break;
        }
    }

    if (m_video_idx == -1) throw std::runtime_error("No video stream found");

    AVCodecParameters* codec_par = m_fmt_ctx->streams[m_video_idx]->codecpar;
    const AVCodec* codec = avcodec_find_decoder(codec_par->codec_id);
    m_codec_ctx = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(m_codec_ctx, codec_par);

    // Ανάκτηση μεταδεδομένων περιστροφής (FFmpeg 4.4+ compatible)
    AVStream* st = m_fmt_ctx->streams[m_video_idx];
    int sd_size = 0;
    uint8_t* sd = av_stream_get_side_data(st, AV_PKT_DATA_DISPLAYMATRIX, &sd_size);
    if (sd && sd_size >= 9 * 4)
    {
        double rot = av_display_rotation_get((int32_t*)sd);
        m_rotation = (int)std::round(rot);
        if (m_rotation < 0) m_rotation += 360;
    }

    // Επιτάχυνση Υλικού (Hardware Acceleration)
    init_hw(AV_HWDEVICE_TYPE_D3D11VA);
    m_codec_ctx->thread_count = std::thread::hardware_concurrency();

    if (avcodec_open2(m_codec_ctx, codec, NULL) < 0)
        throw std::runtime_error("Could not open codec");

    m_frame = av_frame_alloc();
    m_sw_frame = av_frame_alloc();
    m_pkt = av_packet_alloc();

    m_fps = av_q2d(st->avg_frame_rate);
    m_total_frames = (int)st->nb_frames;
    m_duration = (double)m_fmt_ctx->duration / AV_TIME_BASE;
}

Decoder::~Decoder()
{
    if (m_sws_ctx) sws_freeContext(m_sws_ctx);
    av_frame_free(&m_frame);
    av_frame_free(&m_sw_frame);
    av_packet_free(&m_pkt);
    avcodec_free_context(&m_codec_ctx);
    avformat_close_input(&m_fmt_ctx);
    if (m_hw_ctx) av_buffer_unref(&m_hw_ctx);
}

void Decoder::init_hw(AVHWDeviceType type)
{
    if (av_hwdevice_ctx_create(&m_hw_ctx, type, NULL, NULL, 0) < 0)
    {
        std::cerr << "HW Acceleration not available, using CPU." << std::endl;
    }
    else
    {
        m_codec_ctx->hw_device_ctx = av_buffer_ref(m_hw_ctx);
        std::cout << "HW Acceleration enabled." << std::endl;
    }
}

void Decoder::seek_to(double seconds)
{
    int64_t target = (int64_t)(seconds * AV_TIME_BASE);
    if (avformat_seek_file(m_fmt_ctx, -1, INT64_MIN, target, target, 0) < 0)
    {
        std::cerr << "Warning: Could not seek to " << seconds << "s" << std::endl;
    }
    avcodec_flush_buffers(m_codec_ctx);
}

bool Decoder::read_frame(cv::Mat& frame)
{
    while (av_read_frame(m_fmt_ctx, m_pkt) >= 0)
    {
        if (m_pkt->stream_index == m_video_idx)
        {
            if (avcodec_send_packet(m_codec_ctx, m_pkt) >= 0)
            {
                if (avcodec_receive_frame(m_codec_ctx, m_frame) >= 0)
                {
                    AVFrame* src = m_frame;
                    if (src->hw_frames_ctx != nullptr)
                    {
                        av_hwframe_transfer_data(m_sw_frame, m_frame, 0);
                        src = m_sw_frame;
                    }

                    if (!m_sws_ctx)
                    {
                        m_sws_ctx = sws_getContext(
                            src->width, src->height, (AVPixelFormat)src->format,
                            src->width, src->height, AV_PIX_FMT_BGR24,
                            SWS_FAST_BILINEAR, NULL, NULL, NULL
                        );
                    }

                    if (frame.rows != src->height || frame.cols != src->width || frame.type() != CV_8UC3)
                    {
                        frame.create(src->height, src->width, CV_8UC3);
                    }

                    uint8_t* dest[4] = { frame.data, NULL, NULL, NULL };
                    int dest_linesize[4] = { (int)frame.step, 0, 0, 0 };
                    sws_scale(m_sws_ctx, src->data, src->linesize, 0, src->height, dest, dest_linesize);

                    av_packet_unref(m_pkt);
                    return true;
                }
            }
        }
        av_packet_unref(m_pkt);
    }
    return false;
}
