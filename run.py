#!/usr/bin/env python
"""
Simple launcher for Face Attendance System
Run with: python run.py
"""

# FIX #1: SILENCE TENSORFLOW SPAM
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import subprocess
import sys

if __name__ == "__main__":
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Try to use venv Python, fall back to system Python
    venv_python = os.path.join(project_dir, "..", ".venv", "Scripts", "python.exe")
    
    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        # Fall back to system Python
        python_exe = sys.executable
    
    # Run app.py with the appropriate Python
    result = subprocess.run([python_exe, "app.py"])
    sys.exit(result.returncode)
