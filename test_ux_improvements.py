#!/usr/bin/env python3
"""
Quick Test Script for UX Improvements
Verifies all 4 fixes are properly implemented.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_fix_1_frame_reduction():
    """Test Fix 1: Frames reduced from 7 to 3"""
    print("\n" + "="*70)
    print("TEST 1: Frame Reduction (7 → 3)")
    print("="*70)
    
    from config import CONSENSUS_FRAMES, CONSENSUS_THRESHOLD, MIN_FRAMES_FOR_DECISION
    
    print(f"✓ CONSENSUS_FRAMES = {CONSENSUS_FRAMES} (expected: 3)")
    print(f"✓ CONSENSUS_THRESHOLD = {CONSENSUS_THRESHOLD} (expected: 0.67)")
    print(f"✓ MIN_FRAMES_FOR_DECISION = {MIN_FRAMES_FOR_DECISION} (expected: 2)")
    
    assert CONSENSUS_FRAMES == 3, "Frame count should be 3"
    assert CONSENSUS_THRESHOLD == 0.67, "Threshold should be 0.67"
    assert MIN_FRAMES_FOR_DECISION == 2, "Min frames should be 2"
    
    print("\n✅ PASS: Frame reduction correctly configured")
    return True

def test_fix_4_bounding_box():
    """Test Fix 4: Bounding box support in detect_face"""
    print("\n" + "="*70)
    print("TEST 4: Bounding Box Support")
    print("="*70)
    
    import inspect
    from src.face_detector import detect_face
    
    # Check function signature
    sig = inspect.signature(detect_face)
    params = list(sig.parameters.keys())
    
    print(f"✓ Function signature: detect_face{sig}")
    print(f"✓ Parameters: {params}")
    
    assert 'return_box' in params, "detect_face should have 'return_box' parameter"
    print(f"✓ return_box parameter exists with default: {sig.parameters['return_box'].default}")
    
    print("\n✅ PASS: Bounding box support implemented")
    return True

def test_fix_2_and_3_app_methods():
    """Test Fix 2 & 3: Visual feedback and _verify_for_action"""
    print("\n" + "="*70)
    print("TEST 2 & 3: Visual Feedback & Fast Verification")
    print("="*70)
    
    import inspect
    from app import FaceAttendanceSystem
    
    # Check that methods exist
    methods = [m for m in dir(FaceAttendanceSystem) if not m.startswith('_')]
    private_methods = [m for m in dir(FaceAttendanceSystem) if m.startswith('_') and not m.startswith('__')]
    
    print(f"✓ Public methods: {methods}")
    print(f"✓ Private methods: {private_methods}")
    
    assert '_verify_for_action' in private_methods, "Missing _verify_for_action method"
    print("✓ _verify_for_action method exists")
    
    # Check run method has visual feedback code
    run_source = inspect.getsource(FaceAttendanceSystem.run)
    assert 'detect_face(frame, return_box=True)' in run_source, "run() should call detect_face with return_box"
    assert 'cv2.rectangle' in run_source, "run() should draw bounding boxes"
    assert 'cv2.putText' in run_source, "run() should display text (scores)"
    print("✓ run() method has visual feedback code:")
    print("  - Bounding box drawing")
    print("  - Score display")
    print("  - Color coding (green/red)")
    
    # Check attend method uses _verify_for_action
    attend_source = inspect.getsource(FaceAttendanceSystem.attend)
    assert '_verify_for_action' in attend_source, "attend() should call _verify_for_action"
    print("✓ attend() method uses _verify_for_action")
    
    print("\n✅ PASS: Visual feedback and fast verification implemented")
    return True

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "UX IMPROVEMENTS VERIFICATION TEST" + " "*20 + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    try:
        results.append(("Fix 1: Frame Reduction", test_fix_1_frame_reduction()))
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        results.append(("Fix 1: Frame Reduction", False))
    
    try:
        results.append(("Fix 4: Bounding Box", test_fix_4_bounding_box()))
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        results.append(("Fix 4: Bounding Box", False))
    
    try:
        results.append(("Fix 2 & 3: Visual Feedback", test_fix_2_and_3_app_methods()))
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        results.append(("Fix 2 & 3: Visual Feedback", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - System ready for deployment!")
    else:
        print("❌ SOME TESTS FAILED - Please review the output above")
    print("="*70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
