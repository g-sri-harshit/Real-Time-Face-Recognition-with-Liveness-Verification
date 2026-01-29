# 🚀 GETTING STARTED - Step-by-Step

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Register a User
- Press `R` when window appears
- Enter username (e.g., "Alice")
- Look at camera steadily
- Wait for 20 samples to be captured
- Registration complete!

### 4. Mark Attendance
- Press `I` for Punch-In or `O` for Punch-Out
- Look at camera
- System will display result:
  - ✓ ACCEPTED → Attendance marked
  - ✗ REJECTED → Check confidence scores

### 5. View Records
Open `data/attendance.csv` to see all records with decisions.

---

## 🔍 Understanding the System

### What Happens During Registration?
```
[You press R]
    ↓
[Enter name]
    ↓
[System captures 20 face samples over ~10 seconds]
    ↓
[Converts each face to 512-D FaceNet embedding]
    ↓
[Averages all 20 embeddings for stability]
    ↓
[Saves to: data/embeddings/embeddings.npy]
```

### What Happens During Punch-In?
```
[You press I]
    ↓
[System captures 1 live frame]
    ↓
[Detects face (MTCNN)]
    ↓
[Converts to FaceNet embedding]
    ↓
[Compares against all registered users (cosine similarity)]
    ↓
[Calculates liveness score (texture analysis)]
    ↓
[Fuses: 0.7×FaceSim + 0.3×Liveness]
    ↓
[Decision: Accept if all thresholds met]
    ↓
[Log to CSV with full transparency]
```

---

## ✅ Checklist Before First Run

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Webcam/camera connected and working
- [ ] Good lighting in room
- [ ] Enough disk space (~2GB for models)
- [ ] Internet (for first-time model download)

---

## 🎯 Test Workflow

### Phase 1: Register 3 Users (2 min)
```
Press R → Type "alice" → Register
Press R → Type "bob" → Register
Press R → Type "charlie" → Register
```

### Phase 2: Test Recognition (1 min)
```
Each person Press I → System recognizes them
Press O → Punch-Out marked
```

### Phase 3: Test Rejection (30 sec)
```
Someone unregistered Press I
→ System rejects with reason
```

### Phase 4: Check Logs
```
Open data/attendance.csv
See all decisions with confidence scores
```

---

## 🧠 Understanding Confidence Scores

### Example 1: Successful Punch
```
name: alice
face_score: 0.82 (matches Alice well)
liveness_score: 0.85 (face is clearly visible, not spoof)
final_confidence: 0.83 (0.7×0.82 + 0.3×0.85 = 0.831)
status: ACCEPTED ✓
```
→ All thresholds met (0.82 ≥ 0.75 AND 0.83 ≥ 0.80)

### Example 2: Rejected (Bad Lighting)
```
name: bob
face_score: 0.78 (matches Bob)
liveness_score: 0.35 (blurry/low-light detected!)
final_confidence: 0.68 (0.7×0.78 + 0.3×0.35 = 0.681)
status: REJECTED ✗
```
→ Confidence too low (0.68 < 0.80)

### Example 3: Rejected (Wrong Person)
```
name: alice
face_score: 0.62 (weak match to Alice)
liveness_score: 0.88 (face is clear)
final_confidence: 0.71 (0.7×0.62 + 0.3×0.88 = 0.705)
status: REJECTED ✗
```
→ Face similarity too low (0.62 < 0.75)

---

## 🔧 Adjusting Sensitivity

### Make System More Strict (reject more)
Edit `config.py`:
```python
FACE_SIM_THRESHOLD = 0.80      # was 0.75 (stricter)
FINAL_CONF_THRESHOLD = 0.85    # was 0.80 (stricter)
EMB_WEIGHT = 0.8               # was 0.7 (rely more on face)
```

### Make System More Lenient (accept more)
Edit `config.py`:
```python
FACE_SIM_THRESHOLD = 0.70      # was 0.75 (lenient)
FINAL_CONF_THRESHOLD = 0.75    # was 0.80 (lenient)
LIVE_WEIGHT = 0.5              # was 0.3 (less strict on liveness)
```

---

## ⚠️ Common Issues & Fixes

### Issue: "Camera not accessible"
```
Solution:
1. Check camera permissions in Windows Settings
2. Try camera index 1 or 2: change cv2.VideoCapture(0) → cv2.VideoCapture(1)
3. Restart application
```

### Issue: Face detection fails
```
Solution:
1. Improve lighting (use a lamp)
2. Position face 0.5-1.0m from camera
3. Look directly at camera (frontal)
4. Ensure no occlusion (clear face)
```

### Issue: Always rejected even with registered user
```
Solution:
1. Check liveness_score (if < 0.5, lighting is too dark)
2. Improve lighting
3. Stay still during capture (no motion blur)
4. Look directly at camera
5. Increase registration samples: REG_SAMPLES = 30 in config.py
```

### Issue: Slow on first run
```
Normal! System is downloading FaceNet model (~100MB)
Subsequent runs use cached model (instant)
```

---

## 📊 Performance Tips

### For Better Accuracy
1. **Registration**: Capture from different angles (up, down, left, right)
   - Modify: `REG_SAMPLES = 30` for more samples
   
2. **Lighting**: Use consistent, well-lit environment
   - Avoid backlighting
   - No harsh shadows on face

3. **Distance**: Keep 0.5-1.0m from camera
   - Too close: poor face detection
   - Too far: low embedding quality

4. **Stability**: Increase thresholds during registration
   ```python
   FACE_SIM_THRESHOLD = 0.80  # stricter
   FINAL_CONF_THRESHOLD = 0.85
   ```

### For Faster Processing
1. Reduce resolution: Modify `camera.py`
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
   ```

2. Skip every 2nd frame (reduce FPS)
   - Modify `app.py` event loop

---

## 🎓 Learning Path

### Beginner: Just run it
```bash
python app.py
# Register, punch, check CSV
```

### Intermediate: Understand decisions
```
Check face_score, liveness_score, final_confidence
Understand why system accepted/rejected
Adjust thresholds in config.py
```

### Advanced: Modify the system
```
Change embedding model (embedding_model.py)
Improve liveness detection (liveness.py)
Add new features (database.py)
```

---

## 💾 Data Storage

### Where is data stored?
```
data/embeddings/embeddings.npy   ← User embeddings (binary)
data/attendance.csv              ← Attendance log (CSV)
```

### Backup user data
```bash
# Backup embeddings
cp data/embeddings/embeddings.npy data/embeddings/backup.npy

# Export CSV to Excel
# Open data/attendance.csv in Excel, Save As .xlsx
```

### Reset system
```bash
# Delete all registered users
rm data/embeddings/embeddings.npy

# Delete all attendance records
rm data/attendance.csv
# Then restart app.py
```

---

## 🎬 Demo Scenarios

### Scenario 1: Single User
```
Register: You
Punch-In: You → ACCEPTED ✓
Punch-Out: You → ACCEPTED ✓
```

### Scenario 2: Multiple Users
```
Register: Alice, Bob, Charlie
Alice Punch-In → ACCEPTED ✓
Bob Punch-Out → ACCEPTED ✓
Charlie Punch-In → ACCEPTED ✓
```

### Scenario 3: Spoof Attack
```
Register: You
Try with: Printed photo of your face
Result: REJECTED ✗ (liveness score low)
```

### Scenario 4: Lighting Variation
```
Register: You in bright room
Punch-In: In dark room → REJECTED ✗ (liveness_score drops)
Punch-In: Back in bright room → ACCEPTED ✓
```

---

## 📞 Troubleshooting Checklist

Before asking for help, verify:
- [ ] Python 3.8+ installed
- [ ] All `requirements.txt` packages installed
- [ ] Camera working (test in Photos app)
- [ ] Data folder exists (`data/` directory)
- [ ] Attendance CSV initialized
- [ ] Good lighting for face detection
- [ ] No error messages in console

---

## ✨ Next Steps

1. **Run the system**: `python app.py`
2. **Register yourself**: Press `R`
3. **Test attendance**: Press `I` and `O`
4. **Check logs**: Open `data/attendance.csv`
5. **Adjust thresholds**: Edit `config.py` if needed
6. **Explore code**: Read comments in `src/` modules
7. **Interview prep**: Study `README.md` → How to Explain section

---

**Happy recognizing! 🎉**
