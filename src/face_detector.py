# Face Detection Module - MTCNN-based face detection

import cv2
from mtcnn import MTCNN


detector = MTCNN()


def detect_face(frame, return_box=False):
    """
    Detect single face in frame using MTCNN.
    
    Args:
        frame (np.ndarray): Input frame from camera
        return_box (bool): If True, return bounding box coordinates
        
    Returns:
        If return_box=False:
            np.ndarray: Cropped face region or None if no/multiple faces
        If return_box=True:
            tuple: (cropped_face, (x, y, w, h)) or (None, None)
    """
    faces = detector.detect_faces(frame)
    
    # Accept only if exactly one face detected
    if len(faces) != 1:
        if return_box:
            return None, None
        return None
    
    # Extract bounding box coordinates
    x, y, w, h = faces[0]["box"]
    x, y = abs(x), abs(y)
    
    # Crop face region
    face = frame[y:y+h, x:x+w]
    
    if return_box:
        return face, (x, y, w, h)
    return face
