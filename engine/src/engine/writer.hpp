#ifndef WRITER_HPP
#define WRITER_HPP

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>

/**
 * @class Writer
 * @brief Ασύγχρονος εγγραφέας εικόνων με χρήση Thread Pool.
 */
class Writer
{
public:
    /**
     * @brief Κατασκευαστής.
     * @param output_dir Ο φάκελος όπου θα αποθηκεύονται τα frames.
     * @param num_threads Αριθμός threads για το pool.
     * @param extension Το format του αρχείου (π.χ. ".webp", ".jpg").
     */
    Writer(std::string output_dir, int num_threads = 0, std::string extension = ".webp");
    
    /**
     * @brief Καταστροφέας. Διασφαλίζει ότι όλα τα tasks έχουν ολοκληρωθεί.
     */
    ~Writer();

    /**
     * @brief Προσθήκη frame στην ουρά για εγγραφή.
     * @param img Το frame προς αποθήκευση.
     * @param frame_index Ο αριθμός του frame (χρησιμοποιείται για το όνομα του αρχείου).
     */
    void write(const cv::Mat& img, int frame_index);

    /**
     * @brief Μπλοκάρει μέχρι να ολοκληρωθούν όλες οι εκκρεμείς εγγραφές.
     */
    void wait_until_done();

private:
    struct WriteTask
    {
        cv::Mat img;
        std::string filepath;
    };

    void worker_thread();

    std::string m_output_dir;
    std::string m_extension;
    std::vector<std::thread> workers;
    std::queue<WriteTask> tasks;

    std::mutex queue_mutex;
    std::condition_variable condition;
    std::condition_variable wait_condition;
    std::atomic<bool> stop;
    std::atomic<int> active_tasks;
};

#endif // WRITER_HPP
