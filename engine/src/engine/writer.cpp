#include "writer.hpp"
#include <iostream>
#include <algorithm>
#include <iomanip>
#include <sstream>

Writer::Writer(std::string output_dir, int num_threads, std::string extension) 
    : m_output_dir(output_dir), m_extension(extension), stop(false), active_tasks(0)
{
    int actual_threads = num_threads;
    if (actual_threads <= 0)
    {
        unsigned int hw_threads = std::thread::hardware_concurrency();
        actual_threads = (hw_threads > 2) ? hw_threads - 2 : 1;
    }

    for (int i = 0; i < actual_threads; ++i)
    {
        workers.emplace_back(&Writer::worker_thread, this);
    }
}

Writer::~Writer()
{
    wait_until_done();
    {
        std::unique_lock<std::mutex> lock(queue_mutex);
        stop = true;
    }
    condition.notify_all();

    for (std::thread& worker : workers)
    {
        if (worker.joinable()) worker.join();
    }
}

void Writer::write(const cv::Mat& img, int frame_index)
{
    // Δημιουργία filename: frame_000001.webp
    std::stringstream ss;
    ss << m_output_dir << "/frame_" << std::setw(6) << std::setfill('0') << frame_index << m_extension;
    std::string filepath = ss.str();

    {
        std::unique_lock<std::mutex> lock(queue_mutex);
        tasks.push({img.clone(), filepath});
    }
    
    active_tasks++;
    condition.notify_one();
}

void Writer::wait_until_done()
{
    std::unique_lock<std::mutex> lock(queue_mutex);
    wait_condition.wait(lock, [this]() { return tasks.empty() && active_tasks.load() == 0; });
}

void Writer::worker_thread()
{
    while (true)
    {
        WriteTask task;
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            condition.wait(lock, [this]() { return stop || !tasks.empty(); });

            if (stop && tasks.empty()) return;

            task = std::move(tasks.front());
            tasks.pop();
        }

        try
        {
            std::vector<int> params;
            if (m_extension == ".webp")
            {
                params.push_back(cv::IMWRITE_WEBP_QUALITY);
                params.push_back(85);
            }
            else if (m_extension == ".jpg" || m_extension == ".jpeg")
            {
                params.push_back(cv::IMWRITE_JPEG_QUALITY);
                params.push_back(90);
            }

            cv::imwrite(task.filepath, task.img, params);
        }
        catch (const std::exception& e)
        {
            std::cerr << "Write error (" << task.filepath << "): " << e.what() << std::endl;
        }

        active_tasks--;
        if (active_tasks.load() == 0 && tasks.empty())
        {
            wait_condition.notify_all();
        }
    }
}
