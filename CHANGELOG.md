# Changelog

All notable changes to the **Video to ML Suite** will be documented in this file.

## [2.0.0] - 2026-04-26

### Added
- **Guided Mode UX**: A new wizard-driven workflow that guides beginners through the pipeline (Extraction → Annotation → Inspection → Training).
- **Internationalization (i18n)**: Native support for Greek 🇬🇷 and English 🇬🇧 across all modules.
- **Language Toggle**: Real-time language switching from the Dashboard.
- **Progress Tracking**: Dashboard now visually tracks completed steps in Guided Mode.
- **Guided Panels**: Educational sidebars in every module explaining ML concepts like "Train/Val split" and "mAP".
- **Smart Defaults**: Automated configuration for beginners to ensure a successful first training run.
- **Progress Counter**: Real-time annotation counter in the Labeler (e.g., "47 / 200 images labeled").
- **Bypass Mechanism**: Link to skip steps in Guided Mode if the user has prior work.

### Improved
- **Dashboard UI**: Updated layout to accommodate Mode and Language toggles.
- **Dataset Inspector**: Added "Load from default path" helper for easier YAML loading.
- **Training Launcher**: Plain-language descriptions for model sizes (Nano, Small, Medium).

## [1.1.0] - 2026-04-20

### Added
- **Dataset Inspector**: Visual analysis of class distributions and dataset health.
- **Keyframe Interpolation**: Linear interpolation between keyframes in the Labeler.
- **Hardware Acceleration**: D3D11VA support in the C++ extraction engine.

### Fixed
- Fixed memory leak in FFmpeg frame decoding.
- Improved sidebar responsiveness in CustomTkinter.

## [1.0.0] - 2026-04-10

### Added
- Initial release with Orchestrator, Generator, and Labeler.
- C++ Engine integration for high-speed frame extraction.
- Basic YOLOv8 training integration.


