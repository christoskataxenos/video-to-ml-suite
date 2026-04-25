#!/bin/bash
# Video To ML Suite - Linux Build Script

echo "=== BUILDING FOR LINUX ==="

# 1. Build C++ Engine
echo "Compiling C++ Engine..."
mkdir -p engine/build
cd engine/build
cmake ..
make -j$(nproc)
cd ../..

ENGINE_BIN="engine/build/engine"
if [ ! -f "$ENGINE_BIN" ]; then
    echo "ERROR: Engine compilation failed!"
    exit 1
fi

# 2. Install Python Dependencies
echo "Installing Python dependencies..."
pip install pyinstaller ultralytics pyyaml pillow customtkinter

# 3. PyInstaller Bundling
echo "Bundling with PyInstaller..."
pyinstaller --noconfirm --onedir --windowed \
    --name VideoToMLSuite \
    --add-data "generator:generator" \
    --add-data "labeler:labeler" \
    --add-data "inspector:inspector" \
    --add-data "trainer:trainer" \
    --add-data "shared:shared" \
    --add-data "$ENGINE_BIN:engine" \
    orchestrator.py

# 4. Packaging (Optional: Requires fpm)
# To create DEB:
# fpm -s dir -t deb -n videotomlsuite -v 1.0 --prefix /opt/videotomlsuite -C dist/VideoToMLSuite .

echo "=== LINUX BUILD COMPLETE ==="
echo "Output located in dist/VideoToMLSuite"
