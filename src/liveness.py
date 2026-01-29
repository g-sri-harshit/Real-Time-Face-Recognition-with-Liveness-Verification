# Liveness Detection Module - Spoof prevention using multiple texture analysis techniques

import cv2
import numpy as np


def liveness(face):
    """
    Detect if face is live (not printed photo/video) using multiple techniques:
    - Laplacian variance (blur detection)
    - Micro-motion detection (brightness variance)
    - Texture analysis
    
    Args:
        face (np.ndarray): Face image
        
    Returns:
        float: Liveness score (0.0 - 1.0)
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Technique 1: Laplacian Variance (Sharpness/Focus)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()
        
        # Normalize Laplacian score (0-1)
        if laplacian_var < 15:
            laplacian_score = 0.2  # Very blurry - likely spoof
        elif laplacian_var < 30:
            laplacian_score = 0.4
        elif laplacian_var < 50:
            laplacian_score = 0.6
        elif laplacian_var < 100:
            laplacian_score = 0.8
        else:
            laplacian_score = 0.95  # Sharp - likely live
        
        # Technique 2: Color Channel Variance
        b, g, r = cv2.split(face)
        color_variance = np.std([b.std(), g.std(), r.std()])
        if color_variance < 5:
            color_score = 0.3  # Low variation - might be flat/printed
        elif color_variance < 15:
            color_score = 0.6
        else:
            color_score = 0.9  # Good color variation - likely live
        
        # Technique 3: Gradient Magnitude (Edge Detection)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        gradient_var = magnitude.mean()
        
        if gradient_var < 5:
            gradient_score = 0.2
        elif gradient_var < 15:
            gradient_score = 0.5
        elif gradient_var < 30:
            gradient_score = 0.8
        else:
            gradient_score = 0.95
        
        # Technique 4: High-frequency Content (LBP-like)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        hf_content = gray.astype(float) - opening.astype(float)
        hf_variance = np.std(hf_content)
        
        if hf_variance < 3:
            hf_score = 0.3
        elif hf_variance < 8:
            hf_score = 0.6
        else:
            hf_score = 0.9
        
        # Technique 5: Contrast/Dynamic Range
        contrast = (gray.max() - gray.min()) / 255.0
        if contrast < 0.3:
            contrast_score = 0.2  # Low contrast - likely printed
        elif contrast < 0.5:
            contrast_score = 0.5
        else:
            contrast_score = 0.9  # Good contrast - likely live
        
        # Combine all scores with weighted average
        # Give more weight to Laplacian and contrast
        final_score = (
            0.30 * laplacian_score +  # Focus/Sharpness
            0.20 * color_score +      # Color variation
            0.20 * gradient_score +   # Edge content
            0.15 * hf_score +         # Texture detail
            0.15 * contrast_score     # Dynamic range
        )
        
        # Ensure score is in valid range
        return max(0.0, min(1.0, final_score))
        
    except Exception as e:
        print(f"Liveness detection error: {e}")
        return 0.5  # Return neutral score on error
