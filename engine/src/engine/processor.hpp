#ifndef PROCESSOR_HPP
#define PROCESSOR_HPP

#include <opencv2/opencv.hpp>

/**
 * @class Processor
 * @brief Handles frame resizing, auto-rotation, and smart deduplication.
 */
class Processor
{
public:
    Processor(double threshold = 0.005, int target_width = 0, int rotation = 0);
    
    bool process_frame(cv::Mat& frame);

private:
    double m_threshold;
    int m_target_width;
    int m_rotation;
    cv::Mat m_prev_frame;

    double calculate_diff(const cv::Mat& img1, const cv::Mat& img2);
    void apply_rotation(cv::Mat& frame);
};

#endif // PROCESSOR_HPP
