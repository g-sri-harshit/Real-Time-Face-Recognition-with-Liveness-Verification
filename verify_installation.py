#!/usr/bin/env python3
"""
Installation & Verification Script
Run this to verify everything is working
"""

import os
import sys
import subprocess

def main():
    print("\n" + "="*70)
    print("  FACE ATTENDANCE SYSTEM - INSTALLATION VERIFICATION")
    print("="*70 + "\n")
    
    # Check Python version
    print("1. Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor} (required: 3.8+)")
    else:
        print(f"   ✗ Python {sys.version_info.major}.{sys.version_info.minor} (required: 3.8+)")
        return
    
    # Check if requirements.txt exists
    print("\n2. Checking project files...")
    files_to_check = [
        "app.py",
        "config.py",
        "requirements.txt",
        "src/camera.py",
        "src/face_detector.py",
        "src/embedding_model.py",
        "src/recognition.py",
        "src/liveness.py",
        "src/database.py",
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} (missing)")
            all_exist = False
    
    if not all_exist:
        print("\n✗ Some files are missing!")
        return
    
    # Check directories
    print("\n3. Checking directories...")
    dirs = ["data", "data/embeddings", "src"]
    for d in dirs:
        if os.path.isdir(d):
            print(f"   ✓ {d}/")
        else:
            print(f"   ✗ {d}/ (missing)")
    
    # Check pip packages
    print("\n4. Checking required packages...")
    required = [
        "opencv-python",
        "mtcnn",
        "facenet-pytorch",
        "torch",
        "torchvision",
        "scipy",
        "pandas",
        "numpy",
    ]
    
    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        
        for package in required:
            if package.replace("-", "_") in installed or package.replace("_", "-") in installed:
                print(f"   ✓ {package}")
            else:
                print(f"   ⚠ {package} (not installed)")
    except:
        print("   ⚠ Could not verify installed packages")
    
    # Check imports
    print("\n5. Testing critical imports...")
    imports_to_test = [
        ("cv2", "OpenCV"),
        ("mtcnn", "MTCNN"),
        ("torch", "PyTorch"),
        ("scipy", "SciPy"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
    ]
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} (not installed)")
    
    # Check camera
    print("\n6. Testing camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("   ✓ Camera accessible and working")
            else:
                print("   ⚠ Camera accessible but unable to read frame")
            cap.release()
        else:
            print("   ✗ Camera not accessible")
            print("      Try adjusting camera index in src/camera.py (0 → 1 or 2)")
    except Exception as e:
        print(f"   ✗ Camera error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Install dependencies (if not already done):")
    print("   $ pip install -r requirements.txt")
    print("\n2. Run the application:")
    print("   $ python app.py")
    print("\n3. Register a user:")
    print("   • Press 'R' when the window appears")
    print("   • Enter your name")
    print("   • Look at the camera as it captures 20 samples")
    print("\n4. Test attendance:")
    print("   • Press 'I' for Punch-In")
    print("   • Press 'O' for Punch-Out")
    print("\n5. Check results:")
    print("   • Open data/attendance.csv to see logged attendance")
    print("\n6. Read documentation:")
    print("   • START_HERE.md (overview)")
    print("   • GETTING_STARTED.md (quick start)")
    print("   • PROJECT_SUMMARY.md (interview prep)")
    print("   • README.md (complete guide)")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
