#!/usr/bin/env python3
"""
Quick Setup & Run Script for Face Attendance System
Run this to verify all dependencies and start the system
"""

import subprocess
import sys
import os


def check_python_version():
    """Verify Python 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def install_dependencies():
    """Install packages from requirements.txt"""
    print("\n→ Installing dependencies (first run only)...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL
        )
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)


def check_camera():
    """Verify camera access"""
    print("\n→ Checking camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            print("✓ Camera accessible")
        else:
            print("⚠ Camera not detected (try another camera index in app.py)")
    except Exception as e:
        print(f"⚠ Camera check failed: {e}")


def create_directories():
    """Ensure all required directories exist"""
    dirs = [
        "data/embeddings",
        "src"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✓ Directory structure verified")


def main():
    """Run setup and start app"""
    print("\n" + "="*60)
    print("  FACE ATTENDANCE SYSTEM - QUICK START")
    print("="*60)
    
    check_python_version()
    create_directories()
    install_dependencies()
    check_camera()
    
    print("\n" + "="*60)
    print("  STARTING APPLICATION...")
    print("="*60 + "\n")
    
    # Import and run app
    try:
        from app import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
