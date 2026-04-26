# Video to ML Suite (v2.0)

A high-performance, integrated toolkit designed for computer vision researchers and engineers to transform raw video data into production-ready ML datasets. Now upgraded to be accessible for absolute beginners while remaining a powerful tool for experts.

## 🚀 Key Features

- **Dual-Mode UX**: Choose between **Expert Mode** (full control) and **Guided Mode** (wizard-driven, step-by-step pipeline for beginners).
- **Full Internationalization (i18n)**: Native support for both **Greek 🇬🇷** and **English 🇬🇧**, with automatic detection and persistent toggling.
- **In-Tool Guided Workflows**: Educational panels in every module explaining ML concepts (Classes, Train/Val split, Interpolation) as you work.
- **Smart Annotation**: Advanced labeling tool with **Linear Keyframe Interpolation** for rapid dataset creation.
- **High-Performance Engine**: C++ backend utilizing FFmpeg and OpenCV for ultra-fast, hardware-accelerated frame extraction.
- **Automated ML Structure**: One-click generation of YOLOv8/v11 directory structures and `dataset.yaml` files.

## 🛠 Core Modules

1.  **1. FRAME EXTRACTOR (Generator)**: High-efficiency C++ engine. Features Batch processing, movement detection, and automated Train/Val splitting.
2.  **2. IMAGE ANNOTATOR (Labeler)**: Precision labeling tool. Includes resizing handles, object renaming, and keyframe interpolation between frames.
3.  **3. DATASET INSPECTOR**: Diagnostic tool to analyze class distributions and verify dataset health before launching training.
4.  **4. TRAINING LAUNCHER**: Simplified interface for Ultralytics YOLO training with real-time console monitoring.

## 🏗 Technical Architecture

### The Engine (C++)
The core processing is handled by a standalone C++ binary:
- **FFmpeg**: Robust video decoding and hardware-accelerated stream handling (D3D11VA).
- **OpenCV**: Frame processing, resizing, and color space conversions.

### The GUI (Python)
Built with Python 3.12+ and `CustomTkinter` for a premium, desktop-class experience.
- **Orchestrator**: Manages sub-processes and provides a unified dashboard with a **Progress Tracker** in Guided Mode.
- **i18n System**: Centralized string management for seamless language switching across all modules.

## 🚦 Getting Started

### Prerequisites
- Windows 10/11
- Python 3.12+
- C++ Build Tools (for the engine)

### Quick Start
1.  **Install dependencies**: `pip install -r requirements.txt`
2.  **Launch Dashboard**: `python orchestrator.py`
3.  **Choose Your Mode**: Beginners should start in **Guided Mode** to follow the sequential pipeline. Experts can switch to **Expert Mode** for unrestricted access.
4.  **Set Language**: Use the flag toggle in the top-right corner to switch between Greek and English.

## 📜 Documentation
For a detailed guide on the workflow and ML concepts, see [INSTRUCTIONS.md](INSTRUCTIONS.md).
Track project evolution in [CHANGELOG.md](CHANGELOG.md).

---
*Developed by Christos Kataxenos*
