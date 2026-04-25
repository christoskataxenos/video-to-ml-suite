#include "processor.hpp"

Processor::Processor(double threshold, int target_width, int rotation)
    : m_threshold(threshold), m_target_width(target_width), m_rotation(rotation)
{
}

bool Processor::process_frame(cv::Mat& frame)
{
    // 1. Auto Rotation
    apply_rotation(frame);

    // 2. Optional Resize
    if (m_target_width > 0 && frame.cols != m_target_width)
    {
        double aspect = static_cast<double>(frame.rows) / frame.cols;
        int target_height = static_cast<int>(m_target_width * aspect);
        cv::resize(frame, frame, cv::Size(m_target_width, target_height), 0, 0, cv::INTER_LINEAR);
    }

    // 3. Deduplication check
    if (m_prev_frame.empty())
    {
        m_prev_frame = frame.clone();
        return true;
    }

    double diff = calculate_diff(frame, m_prev_frame);
    
    if (diff > m_threshold)
    {
        frame.copyTo(m_prev_frame);
        return true;
    }

    return false;
}

void Processor::apply_rotation(cv::Mat& frame)
{
    // FFmpeg rotation is clockwise. OpenCV rotation is also supported.
    // m_rotation values: 90, 180, 270. (Note: av_display_rotation_get returns counter-clockwise, so we handle it)
    if (m_rotation == 270) {
        cv::rotate(frame, frame, cv::ROTATE_90_CLOCKWISE);
    } else if (m_rotation == 180) {
        cv::rotate(frame, frame, cv::ROTATE_180);
    } else if (m_rotation == 90) {
        cv::rotate(frame, frame, cv::ROTATE_90_COUNTERCLOCKWISE);
    }
}

double Processor::calculate_diff(const cv::Mat& img1, const cv::Mat& img2)
{
    double l1_norm = cv::norm(img1, img2, cv::NORM_L1);
    double total_pixels = static_cast<double>(img1.rows) * img1.cols * img1.channels();
    return l1_norm / (total_pixels * 255.0);
}
