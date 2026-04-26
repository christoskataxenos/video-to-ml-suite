import os
import subprocess
import sys
import shutil

def build_app():
    print("=== VIDEO TO ML SUITE - PACKAGING SYSTEM ===")
    
    # 0. Clean previous builds to ensure fresh code
    folders_to_clean = ["build", "dist"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"Cleaning {folder} folder...")
            shutil.rmtree(folder)
            
    # Also clean the spec file to avoid config conflicts
    spec_file = "VideoToMLSuite.spec"
    if os.path.exists(spec_file):
        print(f"Removing {spec_file}...")
        os.remove(spec_file)
    
    # 1. Detect C++ Engine
    # Check Release first, then Debug
    possible_engine_paths = [
        os.path.join("engine", "build", "Release", "engine.exe"),
        os.path.join("engine", "build", "Debug", "engine.exe"),
        os.path.join("engine", "build", "engine.exe")
    ]
    
    engine_path = None
    for p in possible_engine_paths:
        if os.path.exists(p):
            engine_path = p
            break
            
    if not engine_path:
        print("ERROR: C++ Engine not found. Please build it first using CMake.")
        return

    print(f"Using Engine at: {engine_path}")

    # 2. Run PyInstaller
    print("Starting PyInstaller bundling (this may take a minute)...")
    
    # We use a custom command that ensures all folders are properly mapped
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir", 
        "--windowed",
        "--name", "VideoToMLSuite",
        # Hidden imports for dynamic module loading
        "--hidden-import", "generator.app",
        "--hidden-import", "labeler.app",
        "--hidden-import", "inspector.app",
        "--hidden-import", "trainer.app",
        "--hidden-import", "deployer.app",
        # Syntax: source_folder;target_folder (Windows uses ;)
        "--add-data", "generator;generator",
        "--add-data", "labeler;labeler",
        "--add-data", "inspector;inspector",
        "--add-data", "trainer;trainer",
        "--add-data", "deployer;deployer",
        "--add-data", "shared;shared",
        "--add-data", f"{engine_path};engine",
        "orchestrator.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*50)
        print("🎉 BUILD COMPLETE - STANDALONE FOLDER READY")
        print("="*50)
        print(f"Location: {os.path.abspath('dist/VideoToMLSuite')}")
        print("\nIMPORTANT FOR INNO SETUP:")
        print("1. Close any open Inno Setup compiler windows.")
        print("2. Open 'installer_script.iss' in Inno Setup.")
        print("3. Press 'Compile' (F9).")
        print("4. This will pick up the NEW files from the 'dist' folder.")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"ERROR during bundling: {e}")

if __name__ == "__main__":
    build_app()
