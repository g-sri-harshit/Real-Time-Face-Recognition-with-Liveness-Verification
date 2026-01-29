# Camera Module - Initialize and manage camera input

import cv2


def get_camera():
    """
    Initialize camera capture.
    
    Returns:
        cv2.VideoCapture: Camera object
        
    Raises:
        RuntimeError: If camera not accessible
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Camera not accessible. Check permissions or try a different camera index.")
    return cap
