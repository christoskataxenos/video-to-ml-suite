import os
import subprocess
import sys
import shutil

def build_app():
    print("=== VIDEO TO ML SUITE - PACKAGING SYSTEM ===")
    
    # 1. Ensure C++ Engine is built
    engine_path = os.path.join("engine", "build", "Debug", "engine.exe")
    if not os.path.exists(engine_path):
        print("Building C++ Engine...")
        os.makedirs(os.path.join("engine", "build"), exist_ok=True)
        # Assuming cmake is in path and VS is installed
        subprocess.run(["cmake", ".."], cwd=os.path.join("engine", "build"))
        subprocess.run(["cmake", "--build", "."], cwd=os.path.join("engine", "build"))
    
    if not os.path.exists(engine_path):
        print("ERROR: Could not build C++ Engine. Please build it manually first.")
        return

    # 2. Run PyInstaller
    # --onedir: Creates a folder (better for Windows Installers)
    # --windowed: No console window
    # --add-data: Include sub-modules and engine
    
    print("Starting PyInstaller bundling...")
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir", # Changed to onedir for Inno Setup
        "--windowed",
        "--name", "VideoToMLSuite",
        f"--add-data=generator;generator",
        f"--add-data=labeler;labeler",
        f"--add-data=inspector;inspector",
        f"--add-data=trainer;trainer",
        f"--add-data=shared;shared",
        f"--add-data={engine_path};engine",
        "orchestrator.py"
    ]
    
    subprocess.run(cmd)
    
    print("\n=== BUILD COMPLETE ===")
    print("Your standalone application is in the 'dist' folder.")

if __name__ == "__main__":
    build_app()
