# Use Ubuntu 22.04 as the base image for broad compatibility
FROM ubuntu:22.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for C++ engine and Python GUI
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libopencv-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavdevice-dev \
    python3 \
    python3-pip \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxi6 \
    libxcursor1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libfontconfig1 \
    libxcursor-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build the C++ Engine
RUN mkdir -p engine/build && \
    cd engine/build && \
    cmake .. && \
    make -j$(nproc)

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set environment variables for GUI
ENV DISPLAY=:0

# Default command: launch the orchestrator
CMD ["python3", "orchestrator.py"]
