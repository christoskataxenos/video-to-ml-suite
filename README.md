# Video to ML Suite

A high-performance, integrated toolkit designed for computer vision researchers and engineers to transform raw video data into production-ready ML datasets. This suite streamlines the entire pipeline from frame extraction to model training, focusing on performance, precision, and craftsmanship.

## Overview

The **Video to ML Suite** is a desktop application that orchestrates a set of specialized modules for building datasets, primarily targeting YOLO-based architectures. It combines the ease of a Python-based GUI with the raw power of a C++ processing engine.

## Core Modules

1. **Frame Extractor (C++ Engine)**: A high-efficiency decoder built with FFmpeg and OpenCV. It supports hardware acceleration (D3D11VA) and intelligent frame selection based on movement thresholds to avoid redundant data.
2. **Image Annotator**: A specialized labeling tool with smart interpolation capabilities, allowing users to label keyframes and automatically generate intermediate annotations.
3. **Dataset Inspector**: A diagnostic tool to analyze class distributions, detect corruptions, and verify dataset integrity before training.
4. **Training Launcher**: A simplified interface for launching YOLO training sessions with pre-configured hyperparameters and logging.

## Technical Architecture

### The Engine (C++)
The core processing is handled by a standalone C++ binary located in the `engine/` directory. 
- **FFmpeg**: Used for robust video decoding and hardware-accelerated stream handling.
- **OpenCV**: Used for frame processing, resizing, and color space conversions.
- **Hardware Acceleration**: Utilizes D3D11VA for ultra-fast decoding on modern GPUs.

### The GUI (Python)
The orchestration layer is built with Python 3.12+ using `CustomTkinter` for a modern, industrial-dark aesthetic.
- **Orchestrator**: Manages sub-processes and provides a unified dashboard.
- **Config Management**: Stores global preferences and engine paths in `config.json`.

## Getting Started

### Prerequisites
- Windows 10/11
- CMake (for engine build)
- Python 3.12+
- FFmpeg & OpenCV libraries (handled via vcpkg)

### Building the Engine
```powershell
cd engine
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### Running the Application
```powershell
pip install -r requirements.txt
python orchestrator.py
```

### Running with Docker (Linux/WSL)
If you prefer to run the suite in a containerized environment (supporting X11 forwarding for the GUI):

```bash
# Build and run using docker-compose
docker-compose up --build
```

Make sure you have allowed X11 connections (e.g., `xhost +local:docker`).

## Repository Structure

- `/engine`: C++ source code for the high-performance extraction engine.
- `/launcher`: Python source for the main application entry point.
- `/labeler`: Annotation and interpolation tools.
- `/shared`: Shared assets, icons, and logos.
- `/rules`: Project-specific logic and heuristics.

## Design Philosophy

This project follows an **Industrial Dark** aesthetic: high-contrast, professional themes, and a focus on technical transparency. Every line of code is hand-crafted, avoiding "AI slop" in favor of readable, structured, and well-commented blocks (Greek comments used for internal craftsmanship).

---
*Developed by Christos Kataxenos*
