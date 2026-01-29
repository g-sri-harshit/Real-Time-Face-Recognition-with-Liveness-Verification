# Embedding Model Module - FaceNet-based face embedding generation

# Suppress all logging before importing models
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import torch
from facenet_pytorch import InceptionResnetV1
import ssl
import urllib.request

# Suppress PyTorch progress bars and warnings
import sys
import io

# Fix SSL certificate issue for downloading pretrained models
ssl._create_default_https_context = ssl._create_unverified_context

# Load pretrained FaceNet model - suppress all verbose output
import sys
_stderr = sys.stderr
sys.stderr = io.StringIO()  # Suppress loading messages
model = InceptionResnetV1(pretrained="vggface2").eval()
sys.stderr = _stderr


def get_embedding(face):
    """
    Generate 512-D FaceNet embedding from face image.
    
    Args:
        face (np.ndarray): Face image (BGR)
        
    Returns:
        np.ndarray: 512-D embedding vector
    """
    # Resize to FaceNet input size
    face = cv2.resize(face, (160, 160))
    
    # Convert to tensor and normalize
    face_tensor = torch.tensor(face).permute(2, 0, 1).float().unsqueeze(0)
    
    # Generate embedding
    with torch.no_grad():
        embedding = model(face_tensor).detach().numpy()[0]
    
    return embedding
