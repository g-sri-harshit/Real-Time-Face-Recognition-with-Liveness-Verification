# Recognition Module - Multi-frame consensus verification for robust identification
# 
# PROBLEM: Single-frame face matching can incorrectly accept unregistered faces
# in open-set scenarios (especially with only one registered user). Cosine 
# similarity will always find a "best match" even when similarity is low.
#
# SOLUTION: Collect embeddings from multiple frames (5-7), check if majority
# frames match the same identity with high confidence. This provides robustness
# against single-frame spoofing or transient false matches.

from scipy.spatial.distance import cosine
from collections import Counter


def recognize_single(embedding, db, threshold=0.75):
    """
    Single-frame face recognition.
    
    Args:
        embedding (np.ndarray): Query face embedding
        db (dict): Database of {name: embedding} pairs
        threshold (float): Minimum similarity required for match
        
    Returns:
        tuple: (best_match_name, similarity_score)
               Returns (None, similarity_score) if no match exceeds threshold
    """
    best_name = None
    best_score = 0.0
    
    if not db:
        return None, 0.0
    
    for name, db_embedding in db.items():
        # Calculate cosine similarity (1 - distance)
        similarity = 1 - cosine(embedding, db_embedding)
        
        if similarity > best_score:
            best_score = similarity
            best_name = name
    
    # Only return a match if it exceeds the threshold
    # This prevents false positives by requiring high confidence
    if best_score >= threshold:
        return best_name, best_score
    else:
        return None, best_score


def recognize_consensus(embeddings_list, db, threshold=0.75, consensus_threshold=0.60):
    """
    Multi-frame consensus recognition.
    
    Collects face identifications from multiple frames and requires consensus
    to prevent transient false matches. This is critical for open-set recognition
    where we need to confidently reject unknown faces.
    
    Args:
        embeddings_list (list): List of embeddings from consecutive frames
        db (dict): Database of {name: embedding} pairs
        threshold (float): Minimum similarity per frame
        consensus_threshold (float): Fraction of frames that must agree (0.6 = 60%)
        
    Returns:
        tuple: (final_name, avg_similarity, consensus_score, frame_matches)
               final_name: Identified user or None
               avg_similarity: Average similarity across all frames
               consensus_score: Fraction of frames supporting final decision (0.0-1.0)
               frame_matches: List of (name, similarity) for each frame
    """
    if not embeddings_list or not db:
        return None, 0.0, 0.0, []
    
    frame_matches = []
    identity_votes = []  # Collect identities that pass threshold
    similarities = []    # Collect all similarity scores for averaging
    
    # Analyze each frame
    for emb in embeddings_list:
        best_name = None
        best_score = 0.0
        
        for name, db_embedding in db.items():
            similarity = 1 - cosine(emb, db_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_name = name
        
        frame_matches.append((best_name, best_score))
        similarities.append(best_score)
        
        # Vote for identity only if it exceeds threshold
        if best_score >= threshold:
            identity_votes.append(best_name)
    
    # Calculate consensus: Did majority of frames vote for same identity?
    if not identity_votes:
        # No frames passed threshold - definitely unknown
        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
        return None, avg_sim, 0.0, frame_matches
    
    # Count votes - most common identity
    vote_counts = Counter(identity_votes)
    top_identity, vote_count = vote_counts.most_common(1)[0]
    
    # Consensus score: fraction of frames supporting this identity
    consensus_score = vote_count / len(embeddings_list)
    avg_similarity = sum(similarities) / len(similarities)
    
    # Require >= consensus_threshold (e.g., 60% of frames must agree)
    if consensus_score >= consensus_threshold:
        return top_identity, avg_similarity, consensus_score, frame_matches
    else:
        # Even though some frames matched, consensus wasn't strong enough
        return None, avg_similarity, consensus_score, frame_matches
