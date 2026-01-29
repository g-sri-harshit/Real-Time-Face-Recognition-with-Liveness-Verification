# Face Recognition System - Multi-Frame Consensus Improvements

## Problem Statement

**Open-Set Recognition Vulnerability**: When only one user is registered, the system incorrectly accepts unregistered faces because cosine similarity will always find a "best match," even if the similarity is low or inconsistent.

### Root Cause
- Single-frame face matching decisions are unreliable
- Cosine similarity metric always returns the closest match, regardless of how far it is
- No verification that the match is actually the registered user

---

## Solution: Multi-Frame Consensus Verification

### Architecture Change

#### BEFORE (Vulnerable)
```
Single Frame → Face Detection → Embedding → Compare with DB → Accept/Reject
                                         ↑
                                    Always finds "best match"
                                    regardless of similarity
```

#### AFTER (Robust)
```
7 Frames → Extract Embeddings → Consensus Voting → Threshold Check → Accept/Reject
  ↓             (7 embeddings)      (majority         (strict
Verify            ↓                   agreement)      threshold)
consistency    Vote for identity
across frames    in each frame
               ↓
          Count votes: did 60%+ of frames agree?
```

---

## Implementation Details

### 1. Multi-Frame Collection (`app.py::attend()`)

**Collects 7 consecutive frames instead of 1:**

```python
embeddings = []
liveness_scores = []

# Collect embeddings from multiple frames
while frames_collected < CONSENSUS_FRAMES:  # CONSENSUS_FRAMES = 7
    ret, frame = self.cap.read()
    face = detect_face(frame)
    if face is not None:
        emb = get_embedding(face)
        live_score = liveness(face)
        
        embeddings.append(emb)
        liveness_scores.append(live_score)
```

**Why 7 frames?**
- Balances speed (collects in ~330ms at 30fps) with robustness
- Requires majority (≥4 frames) to agree for acceptance
- Resistant to transient noise or lighting changes

### 2. Consensus Voting (`src/recognition.py::recognize_consensus()`)

**Multi-frame consensus logic:**

```python
def recognize_consensus(embeddings_list, db, threshold=0.75, consensus_threshold=0.60):
    identity_votes = []
    
    # Each frame votes if similarity > threshold
    for emb in embeddings_list:
        for name, db_embedding in db.items():
            similarity = 1 - cosine(emb, db_embedding)
            if similarity >= threshold:
                identity_votes.append(name)  # Vote for this identity
    
    # Consensus: do ≥60% of frames agree?
    if len(identity_votes) >= 0.60 * len(embeddings_list):
        return top_identity, avg_similarity, consensus_score, frame_matches
    else:
        return None, avg_similarity, consensus_score, frame_matches
```

**Key principle:**
- Each frame independently votes based on face similarity
- Only votes for identity if similarity ≥ FACE_SIM_THRESHOLD (0.82)
- Requires ≥60% of frames to vote for same identity
- **Result:** Unknown faces cannot get consistent high-similarity votes

### 3. Stricter Thresholds (Production-Safe)

| Parameter | Before | After | Reasoning |
|-----------|--------|-------|-----------|
| `FACE_SIM_THRESHOLD` | 0.75 | 0.82 | Require stronger face match |
| `LIVENESS_THRESHOLD` | 0.70 | 0.70 | Maintain spoof detection |
| `FINAL_CONF_THRESHOLD` | 0.80 | 0.88 | Higher overall confidence |
| `EMB_WEIGHT` | 0.70 | 0.65 | Balanced weighting |
| `LIVE_WEIGHT` | 0.30 | 0.35 | Stronger liveness check |

### 4. Clear Rejection Categories

**Rejection is now explicit and categorized:**

```python
if name is None:
    # UNKNOWN_FACE: Best match never consistently high
    rejection_category = "UNKNOWN_FACE"
    
elif avg_liveness < LIVENESS_THRESHOLD:
    # SPOOF_DETECTED: Liveness check failed
    rejection_category = "SPOOF_DETECTED"
    
elif final_confidence < FINAL_CONF_THRESHOLD:
    # LOW_CONFIDENCE: Final score below threshold
    rejection_category = "LOW_CONFIDENCE"
```

**Improves debugging:** You can see exactly WHY a face was rejected.

### 5. Duplicate Punch Prevention

**Prevents multiple punch-ins while standing in front of camera:**

```python
# Check if punch was logged in last 60 seconds
if last_key in self.last_attendance:
    time_diff = (current_time - self.last_attendance[last_key]).total_seconds()
    if time_diff < 60 and status == "ACCEPTED":
        print(f"⚠ Already logged {time_diff:.0f}s ago - skipping duplicate")
        return
```

---

## Why This Fixes Open-Set Recognition

### Scenario 1: Registered User (Should Accept ✓)
```
User: Alice (registered with 20 face samples)
Test: Alice's face in front of camera

Frame 1: similarity=0.95 ✓ (vote for Alice)
Frame 2: similarity=0.93 ✓ (vote for Alice)
Frame 3: similarity=0.91 ✓ (vote for Alice)
Frame 4: similarity=0.89 ✓ (vote for Alice)
Frame 5: similarity=0.87 ✓ (vote for Alice)
Frame 6: similarity=0.85 ✓ (vote for Alice)
Frame 7: similarity=0.83 ✓ (vote for Alice)

Consensus: 7/7 frames voted for Alice (100%)
Result: ACCEPTED ✓
```

### Scenario 2: Unregistered User (Should Reject ✗)
```
User: Bob (NOT registered)
Test: Bob's face in front of camera

Frame 1: similarity to Alice=0.65 ✗ (below 0.82 threshold, no vote)
Frame 2: similarity to Alice=0.62 ✗ (no vote)
Frame 3: similarity to Alice=0.67 ✗ (no vote)
Frame 4: similarity to Alice=0.61 ✗ (no vote)
Frame 5: similarity to Alice=0.64 ✗ (no vote)
Frame 6: similarity to Alice=0.63 ✗ (no vote)
Frame 7: similarity to Alice=0.66 ✗ (no vote)

Consensus: 0/7 frames voted for Alice (0%)
REJECTION REASON: UNKNOWN_FACE
Average similarity: 0.64 < 0.82 threshold
Result: REJECTED ✗
```

### Scenario 3: Spoof Attempt with Photo (Should Reject ✗)
```
User: Photo of Alice (printed)
Test: Photo held in front of camera

Frame 1: similarity=0.78, liveness=0.40 ✗ (low liveness)
Frame 2: similarity=0.76, liveness=0.35 ✗ (low liveness)
Frame 3: similarity=0.75, liveness=0.38 ✗ (low liveness)
... (all frames have low liveness)

Consensus: Might get 60%+ votes on identity
BUT liveness check fails: 0.38 < 0.70 threshold
REJECTION REASON: SPOOF_DETECTED
Result: REJECTED ✗
```

---

## Configuration Parameters (config.py)

All magic numbers are now in `config.py` for easy tuning:

```python
# Recognition thresholds
FACE_SIM_THRESHOLD = 0.82          # Min similarity per frame
LIVENESS_THRESHOLD = 0.70          # Min liveness score
FINAL_CONF_THRESHOLD = 0.88        # Min weighted confidence

# Consensus parameters
CONSENSUS_FRAMES = 7               # Frames to collect
CONSENSUS_THRESHOLD = 0.60         # 60% must agree
MIN_FRAMES_FOR_DECISION = 4        # Need 4/7 valid detections

# Confidence weighting
EMB_WEIGHT = 0.65                  # Face embedding weight (65%)
LIVE_WEIGHT = 0.35                 # Liveness weight (35%)
```

**How to tune:**
- **Too many rejections?** Lower `CONSENSUS_THRESHOLD` or `FACE_SIM_THRESHOLD`
- **Too many false acceptances?** Raise thresholds or increase `CONSENSUS_FRAMES`
- **Slow collection?** Lower `CONSENSUS_FRAMES` (but reduces robustness)

---

## Logging & Debugging

### CSV Attendance Record

New column: `rejection_reason`

```
name,time,punch_type,face_score,liveness_score,final_confidence,status,rejection_reason
Alice,2026-01-29 12:00:01,Punch-In,0.91,0.88,0.898,ACCEPTED,
Bob,2026-01-29 12:00:15,Punch-In,0.64,0.80,0.670,REJECTED,UNKNOWN_FACE
Charlie,2026-01-29 12:00:30,Punch-In,0.85,0.35,0.720,REJECTED,SPOOF_DETECTED
```

### Console Output

```
======================================================================
VERIFICATION RESULT
======================================================================
Punch Type:        Punch-In
Identity:          Alice
Frames Analyzed:   7
Consensus Score:   100% (frames agreeing on identity)
Avg Face Sim:      0.91 (threshold: 0.82)
Avg Liveness:      0.88 (threshold: 0.70)
Final Confidence:  0.896 (threshold: 0.88)
Status:            ACCEPTED
======================================================================
```

---

## Performance & Trade-offs

| Aspect | Impact | Mitigation |
|--------|--------|-----------|
| **Speed** | 7 frames = ~230ms delay | Fast enough for real-time |
| **False Negatives** | Registered users rarely rejected | High consistency (0.85+) sim |
| **False Positives** | Unregistered users reliably rejected | Multi-frame + strict threshold |
| **Spoofing Resistance** | Strong (multi-frame + liveness) | Two independent checks |

---

## System Behavior Summary

| Input | Output | Reason |
|-------|--------|--------|
| Registered user | ACCEPTED | High consensus + confidence |
| Unregistered person | REJECTED | No consensus on high similarity |
| Printed photo | REJECTED | Liveness check fails |
| Video replay | REJECTED | Liveness check fails |
| Registered user with glasses | ACCEPTED* | If still >60% consensus |
| Registered user in different light | ACCEPTED* | If still >60% consensus |

*Depends on registration quality (20 samples capture variation)

---

## Testing the System

### Test Case 1: Register Known User
```
Press R → Capture 20 face samples → Average embeddings → Store
```

### Test Case 2: Accept Registered User
```
Press I → Collect 7 frames → All frames match with >0.82 sim
→ 100% consensus → ACCEPTED
```

### Test Case 3: Reject Unregistered User
```
Press I → Collect 7 frames → All frames have <0.82 sim
→ 0% consensus → REJECTED (UNKNOWN_FACE)
```

### Test Case 4: Reject Spoof
```
Press I with printed photo → Liveness check fails
→ REJECTED (SPOOF_DETECTED)
```

---

## Code Comments Explaining Security

Look for these comments in the code:

1. **`src/recognition.py`** - Multi-frame consensus logic
   ```python
   # PROBLEM: Single-frame face matching can incorrectly accept
   # unregistered faces in open-set scenarios...
   ```

2. **`app.py::attend()`** - Collection and verification
   ```python
   # This prevents the open-set recognition problem where
   # unregistered faces get accepted as the "closest match"
   ```

3. **`app.py::_log_attendance()`** - Duplicate prevention
   ```python
   # Prevent duplicate punches for same user in quick succession
   ```

---

## References

- **Open-Set Recognition Problem**: Faces in unconstrained datasets
- **Multi-Frame Consensus**: Used in production face unlock systems
- **Cosine Similarity Pitfall**: Always returns closest match (not necessarily good match)
- **Liveness Detection**: Essential for spoof prevention

---

## Conclusion

This refactoring converts the system from vulnerable single-frame matching to robust multi-frame consensus verification. The system now:

✅ **Reliably rejects unregistered users** (open-set robustness)  
✅ **Maintains high acceptance for registered users** (sensitivity)  
✅ **Detects spoofing attempts** (liveness + multi-frame)  
✅ **Provides clear rejection reasons** (debugging & explainability)  
✅ **Prevents duplicate punches** (business logic)  
✅ **Production-safe thresholds** (configurable, conservative)  

**Result:** A face recognition attendance system that is both reliable and maintainable.
