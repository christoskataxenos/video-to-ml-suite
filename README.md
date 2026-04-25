# Video to ML Suite

A high-performance, integrated toolkit designed for computer vision researchers and engineers to transform raw video data into production-ready ML datasets. This suite streamlines the entire pipeline from frame extraction to model training, focusing on performance, precision, and craftsmanship.

## 🚀 Key Features

- **Industrial UI/UX**: Professional Dark Mode with Neon Cyan accents and persistent instructional sidebars.
- **Smart Annotation**: Advanced labeling tool with **Linear Keyframe Interpolation** for rapid dataset creation.
- **High-Performance Engine**: C++ backend utilizing FFmpeg and OpenCV for ultra-fast, hardware-accelerated frame extraction.
- **Automated ML Structure**: One-click generation of YOLOv8/v11 directory structures and `dataset.yaml` files.
- **Integrated Workflow**: A unified Orchestrator that manages the transition between extraction, labeling, inspection, and training.

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
- **Orchestrator**: Manages sub-processes and provides a unified dashboard.
- **UX Consistency**: Standardized help panels in every module to guide the user step-by-step.

## 🚦 Getting Started

### Prerequisites
- Windows 10/11
- Python 3.12+
- C++ Build Tools (for the engine)

### Quick Start
1.  **Install dependencies**: `pip install -r requirements.txt`
2.  **Launch Dashboard**: `python orchestrator.py`
3.  **Follow the Guide**: Each module contains a left sidebar with specific instructions.

## 📜 Documentation
For a detailed guide on how to build a model from scratch, see [INSTRUCTIONS.md](INSTRUCTIONS.md).

---
*Developed by Christos Kataxenos*
