# PolyMind — Design Specification v1.0

## 1. High-Level Architecture

PolyMind is designed as a **Client-Server** web application. This architecture supports local execution on a PC/Laptop and remote execution via Docker/Proxmox, accessible from any browser-enabled device (PC, Tablet, Raspberry Pi).

### Tech Stack
- **Backend**: Python (FastAPI)
  - Fast, modern, and provides automatic API documentation.
  - Handles ML logic, file system operations, and communication with the C++ engine.
- **Frontend**: Next.js (React)
  - Powerful UI/UX capabilities for animations, mascots, and high-quality "kid-friendly" visuals.
  - Server-Side Rendering (SSR) options for better performance on low-power devices (like older tablets/Pi).
- **Engine**: Existing C++ Extraction Engine
  - Reused via subprocess calls from the Python backend.
- **Database**: SQLite (local)
  - Simple, file-based database for storing progress, mascots settings, and language preferences.
- **Containerization**: Docker
  - Multi-stage build for easy deployment on home servers (Proxmox/Docker).

### Data Flow
1. **User Action**: Child interacts with the Web UI (Sticker Mode).
2. **API Request**: Frontend sends coordinates/actions to the FastAPI backend.
3. **Engine/ML Execution**: Backend triggers the C++ engine for frames or Ultralytics for training.
4. **Real-time Feedback**: WebSockets (FastAPI) push progress updates (progress bars, mascot voices) back to the UI.

Does this architecture look right so far?
