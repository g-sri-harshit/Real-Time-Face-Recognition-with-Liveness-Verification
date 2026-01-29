# 🚀 HOW TO RUN THE PROJECT

The virtual environment is **AUTOMATICALLY HARDCODED** into the project. 

Use **any one** of these methods to run the system:

---

## Method 1: Batch File (Easiest - Windows)

### Double-Click This File:
```
run.bat
```

**What it does:**
- Automatically activates the virtual environment
- Launches the Face Attendance System
- No terminal commands needed

---

## Method 2: PowerShell (Recommended)

### Run This Command:
```powershell
.\run.ps1
```

**Or Right-Click & Select "Run with PowerShell"**

**What it does:**
- Activates venv in PowerShell
- Starts the application
- Shows activation confirmation

---

## Method 3: Python Direct (Any Terminal)

### Run:
```bash
python quick_run.py
```

**What it does:**
- Auto-detects venv
- Automatically activates it
- Runs the application
- Works from any terminal

---

## Method 4: Manual Terminal

### Open PowerShell/CMD in project folder and run:

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

**Command Prompt (CMD):**
```cmd
venv\Scripts\activate.bat
python app.py
```

---

## ✅ Virtual Environment Details

### Location:
```
face-attendance-system/venv/
```

### What's Inside:
- ✓ Python 3.10
- ✓ All required packages
- ✓ OpenCV
- ✓ PyTorch
- ✓ FaceNet
- ✓ TensorFlow (for MTCNN)
- ✓ All dependencies

### Automatic Activation:
The venv is **hardcoded** into:
- `run.bat` (batch script)
- `run.ps1` (PowerShell script)
- `quick_run.py` (Python launcher)

Just use one of the above, and venv activates **automatically**.

---

## 🎮 Once the App Starts

You'll see the live camera window with:
```
Press R → Register new user
Press I → Punch-In
Press O → Punch-Out
Press Q → Quit
```

---

## 🆘 If Something Goes Wrong

### Venv not activating?
Try: `python quick_run.py`

### Still having issues?
```bash
# Manually recreate venv
python -m venv venv

# Install packages
.\venv\Scripts\pip install -r requirements.txt

# Run
.\venv\Scripts\python app.py
```

---

## 📝 Project Structure with Venv

```
face-attendance-system/
├── venv/                    ← Virtual environment (HARDCODED)
│   ├── Scripts/
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   └── Activate.ps1
│   └── Lib/                 ← All packages installed here
│
├── run.bat                  ← Double-click to run (Windows)
├── run.ps1                  ← PowerShell launcher
├── quick_run.py             ← Python launcher
│
├── app.py                   ← Main application
├── config.py                ← Configuration
├── requirements.txt         ← Package list
│
├── src/                     ← Core modules
├── data/                    ← Runtime data
│
└── [Documentation files]
```

---

## ✨ Quick Reference

| Task | Command |
|------|---------|
| Run (Windows) | `run.bat` (double-click) |
| Run (PowerShell) | `.\run.ps1` |
| Run (Any Terminal) | `python quick_run.py` |
| Manual Run | `.\venv\Scripts\Activate.ps1` then `python app.py` |
| Check Venv | `.\venv\Scripts\python --version` |

---

**The virtual environment is always active when you use the launcher scripts!** ✅
