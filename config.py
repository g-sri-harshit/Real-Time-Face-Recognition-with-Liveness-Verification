# Face Attendance System Configuration
# Production-safe thresholds and multi-frame consensus strategy

# ============================================================================
# RECOGNITION THRESHOLDS - Mitigates open-set recognition false positives
# ============================================================================
FACE_SIM_THRESHOLD = 0.82      # Strict similarity threshold (>= required)
LIVENESS_THRESHOLD = 0.70      # Minimum liveness score to pass spoof detection
FINAL_CONF_THRESHOLD = 0.88    # Final confidence must exceed this for acceptance

# ============================================================================
# MULTI-FRAME CONSENSUS VERIFICATION
# Addresses open-set recognition problem by requiring consistency across frames
# Single-frame decisions can be fooled; majority consensus is more robust
# ============================================================================
CONSENSUS_FRAMES = 3           # Reduced from 7 for UX: ~100ms verification
CONSENSUS_THRESHOLD = 0.67     # Require 2 out of 3 frames to match (67%)
MIN_FRAMES_FOR_DECISION = 2    # Need minimum 2 valid detections from 3 frames

# ============================================================================
# CONFIDENCE WEIGHTING
# ============================================================================
EMB_WEIGHT = 0.65              # Face embedding similarity weight (65%)
LIVE_WEIGHT = 0.35             # Liveness detection weight (35%)

# ============================================================================
# REGISTRATION & SAMPLING
# ============================================================================
STABLE_FRAMES = 5              # Frames required for stable detection
REG_SAMPLES = 20               # Samples per user during registration
REG_LIVENESS_MIN = 0.75        # Minimum liveness score during registration

# ============================================================================
# DATABASE PATHS
# ============================================================================
EMBEDDINGS_PATH = "data/embeddings/embeddings.npy"
ATTENDANCE_CSV = "data/attendance.csv"

# ============================================================================
# DECISION REJECTION CATEGORIES
# Used for clear logging and debugging of why a face was rejected
# ============================================================================
REJECTION_UNKNOWN = "UNKNOWN_FACE"         # Face doesn't match any user
REJECTION_LOW_SIM = "LOW_SIMILARITY"       # Similarity below threshold
REJECTION_LOW_CONF = "LOW_CONFIDENCE"      # Final confidence below threshold
REJECTION_LOW_LIVE = "SPOOF_DETECTED"      # Liveness score too low
