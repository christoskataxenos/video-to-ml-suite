#ifndef DECODER_HPP
#define DECODER_HPP

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/imgutils.h>
#include <libavutil/display.h>
#include <libswscale/swscale.h>
}

/**
 * @class Decoder
 * @brief High-performance video decoder using FFmpeg with HW acceleration support.
 */
class Decoder
{
public:
    Decoder(const std::string& filepath);
    ~Decoder();

    bool read_frame(cv::Mat& frame);
    
    // Seek to specific time (seconds)
    void seek_to(double seconds);

    double get_fps() const { return m_fps; }
    int get_total_frames() const { return m_total_frames; }
    double get_duration() const { return m_duration; }
    int get_rotation() const { return m_rotation; }

private:
    void init_hw(AVHWDeviceType type);

    AVFormatContext* m_fmt_ctx = nullptr;
    AVCodecContext* m_codec_ctx = nullptr;
    AVBufferRef* m_hw_ctx = nullptr;
    AVFrame* m_frame = nullptr;
    AVFrame* m_sw_frame = nullptr;
    AVPacket* m_pkt = nullptr;
    struct SwsContext* m_sws_ctx = nullptr;

    int m_video_idx = -1;
    double m_fps = 0.0;
    int m_total_frames = 0;
    double m_duration = 0.0;
    int m_rotation = 0;
};

#endif // DECODER_HPP
