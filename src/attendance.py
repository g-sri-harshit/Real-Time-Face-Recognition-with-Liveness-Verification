# Database Module - Embedding storage and retrieval

import numpy as np
import os


EMBEDDINGS_PATH = "data/embeddings/embeddings.npy"


def load_db():
    """
    Load embedding database from disk.
    
    Returns:
        dict: {name: embedding} pairs or empty dict if file doesn't exist
    """
    if os.path.exists(EMBEDDINGS_PATH):
        return np.load(EMBEDDINGS_PATH, allow_pickle=True).item()
    return {}


def save_db(db):
    """
    Save embedding database to disk.
    
    Args:
        db (dict): {name: embedding} pairs
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
    np.save(EMBEDDINGS_PATH, db)
