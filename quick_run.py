#!/usr/bin/env python
"""
Quick Launcher - Automatically activates venv and runs the app
Just run: python quick_run.py
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("  FACE RECOGNITION ATTENDANCE SYSTEM - AUTO LAUNCHER")
print("="*70 + "\n")

# Determine Python executable in venv
venv_python = os.path.join("venv", "Scripts", "python.exe")

if not os.path.exists(venv_python):
    print("✗ Virtual environment not found!")
    print("  Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✓ Virtual environment created")
    
    print("\n✓ Installing dependencies...")
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✓ Dependencies installed")

print("\n✓ Virtual environment ready")
print("✓ Starting application...\n")

# Run app in venv
subprocess.run([venv_python, "app.py"])
