cmake_minimum_required(VERSION 3.20)
project(video-to-jpeg LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Find FFmpeg via PkgConfig
find_package(PkgConfig REQUIRED)
pkg_check_modules(AVCODEC REQUIRED libavcodec)
pkg_check_modules(AVFORMAT REQUIRED libavformat)
pkg_check_modules(AVUTIL REQUIRED libavutil)
pkg_check_modules(SWSCALE REQUIRED libswscale)

# Προσθήκη των φακέλων των βιβλιοθηκών για τον Linker (ειδικά για Windows/vcpkg)
link_directories(
    ${AVCODEC_LIBRARY_DIRS}
    ${AVFORMAT_LIBRARY_DIRS}
    ${AVUTIL_LIBRARY_DIRS}
    ${SWSCALE_LIBRARY_DIRS}
)

include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${AVCODEC_INCLUDE_DIRS}
    ${AVFORMAT_INCLUDE_DIRS}
    ${AVUTIL_INCLUDE_DIRS}
    ${SWSCALE_INCLUDE_DIRS}
    src/engine
)

add_executable(engine
    src/engine/main.cpp
    src/engine/decoder.cpp
    src/engine/processor.cpp
    src/engine/writer.cpp
)

# Σύνδεση με τις βιβλιοθήκες χρησιμοποιώντας τα πλήρη LDFLAGS ή τα ονόματα
target_link_libraries(engine
    PRIVATE
    ${OpenCV_LIBS}
    ${AVCODEC_LIBRARIES}
    ${AVFORMAT_LIBRARIES}
    ${AVUTIL_LIBRARIES}
    ${SWSCALE_LIBRARIES}
)

# Compilation Flags
if(MSVC)
    target_compile_options(engine PRIVATE /W3 /Ot /arch:AVX2)
else()
    target_compile_options(engine PRIVATE -Wall -Wextra -O3 -mavx2)
endif()
