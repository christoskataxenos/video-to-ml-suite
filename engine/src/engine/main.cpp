#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <chrono>
#include <opencv2/opencv.hpp>
#include "decoder.hpp"
#include "processor.hpp"
#include "writer.hpp"

namespace fs = std::filesystem;
using namespace std::chrono;

struct Config
{
    std::string input_path;
    std::string output_dir = "./frames";
    double threshold = 0.005;
    std::string format = ".jpg";
    int target_fps = 0;
    int resize_width = 0;
    double start_time = 0.0;
    double end_time = -1.0;
};

// Απλός Base64 encoder για τα thumbnails
std::string base64_encode(const std::vector<uchar>& data) {
    static const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string out;
    int val = 0, valb = -6;
    for (uchar c : data) {
        val = (val << 8) + c;
        valb += 8;
        while (valb >= 0) {
            out.push_back(chars[(val >> valb) & 0x3F]);
            valb -= 6;
        }
    }
    if (valb > -6) out.push_back(chars[((val << 8) >> (valb + 8)) & 0x3F]);
    while (out.size() % 4) out.push_back('=');
    return out;
}

void print_welcome()
{
    std::cout << "--- PAPATZIS SPOTER v0.1 ---" << std::endl;
}

void parse_args(int argc, char* argv[], Config& cfg)
{
    if (argc < 2) return;
    cfg.input_path = argv[1];

    for (int i = 2; i < argc; i++)
    {
        std::string arg = argv[i];
        if (arg == "--output" && i + 1 < argc) cfg.output_dir = argv[++i];
        else if (arg == "--threshold" && i + 1 < argc) cfg.threshold = std::stod(argv[++i]);
        else if (arg == "--format" && i + 1 < argc) cfg.format = argv[++i];
        else if (arg == "--fps" && i + 1 < argc) cfg.target_fps = std::stoi(argv[++i]);
        else if (arg == "--resize" && i + 1 < argc) cfg.resize_width = std::stoi(argv[++i]);
        else if (arg == "--start" && i + 1 < argc) cfg.start_time = std::stod(argv[++i]);
        else if (arg == "--end" && i + 1 < argc) cfg.end_time = std::stod(argv[++i]);
    }
}

int main(int argc, char* argv[])
{
    auto start_total = high_resolution_clock::now();
    print_welcome();

    Config cfg;
    if (argc < 2)
    {
        std::cerr << "Usage: engine <input_video> [options]" << std::endl;
        return 1;
    }

    parse_args(argc, argv, cfg);

    if (!fs::exists(cfg.output_dir))
    {
        fs::create_directories(cfg.output_dir);
    }

    try
    {
        Decoder decoder(cfg.input_path);
        
        // Εφαρμογή περικοπής (Trimming)
        if (cfg.start_time > 0) decoder.seek_to(cfg.start_time);
        double duration = decoder.get_duration();
        if (cfg.end_time < 0 || cfg.end_time > duration) cfg.end_time = duration;

        Processor processor(cfg.threshold, cfg.resize_width, decoder.get_rotation());
        
        int num_threads = std::max(1, static_cast<int>(std::thread::hardware_concurrency()) - 2);
        Writer writer(cfg.output_dir, num_threads, cfg.format);

        std::cout << "Engine initialized. Duration: " << duration << "s" << std::endl;
        if (decoder.get_rotation() != 0) std::cout << "Auto-rotation detected: " << decoder.get_rotation() << "deg" << std::endl;

        int frame_count = 0;
        int saved_count = 0;
        int skipped_count = 0;
        int total_frames = decoder.get_total_frames();

        cv::Mat frame;
        double video_fps = decoder.get_fps();
        int frame_interval = (cfg.target_fps > 0) ? static_cast<int>(video_fps / cfg.target_fps) : 1;
        if (frame_interval < 1) frame_interval = 1;

        auto start_analysis = high_resolution_clock::now();
        auto last_thumb_time = high_resolution_clock::now();

        while (decoder.read_frame(frame))
        {
            double current_time = frame_count / video_fps + cfg.start_time;
            if (current_time > cfg.end_time) break;

            frame_count++;

            if (frame_count % frame_interval != 0)
            {
                skipped_count++;
                continue;
            }

            if (processor.process_frame(frame))
            {
                writer.write(frame, saved_count);
                saved_count++;

                // Αποστολή Thumbnail στο GUI (μέγιστο 5 fps για προεπισκόπηση)
                auto now = high_resolution_clock::now();
                if (duration_cast<milliseconds>(now - last_thumb_time).count() > 200)
                {
                    cv::Mat thumb;
                    cv::resize(frame, thumb, cv::Size(320, 180), 0, 0, cv::INTER_NEAREST);
                    std::vector<uchar> buf;
                    cv::imencode(".jpg", thumb, buf);
                    std::cout << "THUMB:" << base64_encode(buf) << std::endl;
                    last_thumb_time = now;
                }
            }
            else
            {
                skipped_count++;
            }

            if (frame_count % 10 == 0)
            {
                std::cout << "PROGRESS:" << frame_count << "/" << total_frames 
                          << ":" << saved_count << ":" << skipped_count << std::endl;
            }
        }

        auto end_analysis = high_resolution_clock::now();
        double analysis_time = duration_cast<milliseconds>(end_analysis - start_analysis).count() / 1000.0;
        std::cout << "REPORT: Analysis completed in " << analysis_time << " seconds." << std::endl;

        writer.wait_until_done();
        
        auto end_total = high_resolution_clock::now();
        double total_time = duration_cast<milliseconds>(end_total - start_total).count() / 1000.0;

        std::cout << "SUCCESS: Extraction finished in " << total_time << " seconds." << std::endl;
        std::cout << "Total processed: " << frame_count << std::endl;
        std::cout << "Saved: " << saved_count << std::endl;
        std::cout << "Skipped: " << skipped_count << std::endl;
    }
    catch (const std::exception& e)
    {
        std::cerr << "CRITICAL ERROR: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
