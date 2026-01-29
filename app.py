"""
Face Recognition Attendance System - Multi-Frame Consensus Verification
Robust, real-time event-driven system with production-safe thresholds.

Controls:
    r -> Register new user
    i -> Punch-In
    o -> Punch-Out
    q -> Quit
"""

# FIX #1: SILENCE TENSORFLOW SPAM - Set ALL logging levels
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF C++ warnings
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# Suppress all warnings
import warnings
warnings.filterwarnings('ignore')

import cv2
import numpy as np
from datetime import datetime
import pandas as pd
import time

# Suppress TensorFlow and Keras logging
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Also suppress Keras verbose output
import keras
keras.utils.disable_interactive_logging()

# Import configuration
from config import (
    FACE_SIM_THRESHOLD,
    LIVENESS_THRESHOLD,
    FINAL_CONF_THRESHOLD,
    EMB_WEIGHT,
    LIVE_WEIGHT,
    REG_SAMPLES,
    REG_LIVENESS_MIN,
    ATTENDANCE_CSV,
    CONSENSUS_FRAMES,
    CONSENSUS_THRESHOLD,
    MIN_FRAMES_FOR_DECISION,
    REJECTION_UNKNOWN,
    REJECTION_LOW_SIM,
    REJECTION_LOW_CONF,
    REJECTION_LOW_LIVE,
)

# Import all modules
from src.camera import get_camera
from src.face_detector import detect_face
from src.embedding_model import get_embedding
from src.recognition import recognize_single, recognize_consensus
from src.liveness import liveness
from src.database import load_db, save_db


# ============================================================================
# UI/UX HELPER FUNCTIONS - Professional Biometric Visualization
# ============================================================================

def draw_status_banner(img, text, level="info"):
    """
    Draw soft status banner at top of frame.
    Levels: 'info' (amber), 'warn' (orange), 'ok' (green)
    """
    h, w = img.shape[:2]
    colors = {
        "info": (200, 165, 0),    # Cyan-amber
        "warn": (0, 165, 255),    # Orange
        "ok":   (0, 200, 100)     # Green
    }
    color = colors.get(level, colors["info"])
    
    # Dark background
    cv2.rectangle(img, (0, 0), (w, 50), (30, 30, 30), -1)
    # Border
    cv2.rectangle(img, (0, 0), (w, 50), color, 2)
    # Text
    cv2.putText(img, text, (20, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def draw_biometric_frame(img, x, y, w, h, color=(255, 255, 0), thickness=2):
    """
    Draw FaceID-style corner brackets (not rectangles).
    Creates distinctive biometric aesthetic.
    """
    t = thickness
    l = int(min(w, h) * 0.25)  # Corner bracket length
    
    # Top-left
    cv2.line(img, (x, y), (x+l, y), color, t)
    cv2.line(img, (x, y), (x, y+l), color, t)
    
    # Top-right
    cv2.line(img, (x+w, y), (x+w-l, y), color, t)
    cv2.line(img, (x+w, y), (x+w, y+l), color, t)
    
    # Bottom-left
    cv2.line(img, (x, y+h), (x+l, y+h), color, t)
    cv2.line(img, (x, y+h), (x, y+h-l), color, t)
    
    # Bottom-right
    cv2.line(img, (x+w, y+h), (x+w-l, y+h), color, t)
    cv2.line(img, (x+w, y+h), (x+w, y+h-l), color, t)


def draw_scanning_line(img, x, y, w, h, frame_id, color=(255, 255, 0)):
    """
    Draw animated scanning line for biometric feel.
    Guides user to hold steady during capture.
    """
    scan_y = y + (frame_id % h)
    cv2.line(img, (x, scan_y), (x+w, scan_y), color, 1)


def draw_confidence_meter(img, center_x, center_y, confidence, radius=32):
    """
    Draw circular confidence meter with arc indicator.
    Visual representation of recognition confidence.
    """
    # Background circle
    cv2.circle(img, (center_x, center_y), radius, (70, 70, 70), 2)
    
    # Confidence arc (0-360 degrees based on confidence)
    angle = int(360 * confidence)
    cv2.ellipse(img, (center_x, center_y), (radius, radius),
               0, 0, angle, (0, 255, 0), 4)
    
    # Percentage text
    pct_text = f"{int(confidence*100)}%"
    cv2.putText(img, pct_text, (center_x-18, center_y+6),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def draw_identity_badge(img, x, y, w, h, name):
    """
    Draw professional identity badge below face.
    Dark background with cyan text.
    """
    badge_y = y + h + 5
    cv2.rectangle(img, (x, badge_y), (x+w, badge_y+30), (30, 30, 30), -1)
    cv2.rectangle(img, (x, badge_y), (x+w, badge_y+30), (200, 150, 50), 1)
    cv2.putText(img, f"ID: {name}", (x+10, badge_y+22),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2)


class FaceAttendanceSystem:
    """
    Multi-frame consensus face recognition system.
    
    Key innovation: Collects embeddings from multiple frames and requires
    majority agreement on identity. This prevents the open-set recognition
    problem where unregistered faces get accepted as the "closest match".
    """
    
    def __init__(self):
        """Initialize the system."""
        print("\n" + "="*60)
        print("  FACE RECOGNITION ATTENDANCE SYSTEM")
        print("  Multi-Frame Consensus Verification")
        print("="*60 + "\n")
        
        try:
            self.cap = get_camera()
            print("[+] Camera initialized")
        except RuntimeError as e:
            print(f"[-] Error: {e}")
            raise
        
        self.db = load_db()
        print(f"[+] Database loaded ({len(self.db)} users registered)")
        
        # Initialize attendance CSV if not exists
        self._init_csv()
        print("[+] Attendance system ready\n")
        
        # FIX #3: COOLDOWN - prevent rapid duplicate punches
        self.last_action_time = 0
        self.COOLDOWN = 3  # seconds between allowed actions
        
        # Track last attendance per user to prevent duplicate punches
        # Format: {(user, punch_type): timestamp}
        self.last_attendance = {}
        
        self._print_controls()
    
    def _init_csv(self):
        """Initialize attendance CSV file."""
        if not os.path.exists(ATTENDANCE_CSV):
            os.makedirs(os.path.dirname(ATTENDANCE_CSV), exist_ok=True)
            df = pd.DataFrame(columns=[
                "name", "time", "punch_type", 
                "face_score", "liveness_score", "final_confidence", "status"
            ])
            df.to_csv(ATTENDANCE_CSV, index=False)
    
    def _print_controls(self):
        """Print control instructions."""
        print("\n" + "-"*60)
        print("KEYBOARD CONTROLS:")
        print("-"*60)
        print("  [R] -> Register new user")
        print("  [I] -> Punch-In")
        print("  [O] -> Punch-Out")
        print("  [Q] -> Quit")
        print("-"*60 + "\n")
    
    def _verify_for_action(self, punch_type):
        """
        Fast verification for action (punch-in/out).
        Collects exactly CONSENSUS_FRAMES with detected faces, then STOPS.
        No unnecessary looping - exits as soon as 3 frames collected.
        
        Returns:
            tuple: (name, face_score, liveness_score, final_confidence)
                   or (None, 0, 0, 0) if verification fails
        """
        names = []
        scores = []
        lives = []
        frames_collected = 0
        
        print(f"-> {punch_type}... Detecting face...")
        
        # Collect exactly CONSENSUS_FRAMES with detected faces
        while frames_collected < CONSENSUS_FRAMES:
            ret, frame = self.cap.read()
            
            if not ret:
                print("✗ Camera read error")
                return None, 0, 0, 0
            
            # Detect face (FAST - skip if not found)
            face, box = detect_face(frame, return_box=True)
            if face is None:
                continue  # Skip frames without faces
            
            # Found a face - process it
            frames_collected += 1
            
            # Get embedding and recognition
            emb = get_embedding(face)
            name, face_score = recognize_single(emb, self.db, threshold=FACE_SIM_THRESHOLD)
            liveness_score = liveness(face)
            
            # Record result
            if name:
                names.append(name)
                scores.append(face_score)
                lives.append(liveness_score)
            else:
                names.append("UNKNOWN")
                scores.append(face_score if face_score > 0 else 0.0)
                lives.append(liveness_score)
            
            # Show feedback (very brief) with professional UX
            x, y, w, h = box
            label = name if name else "Unknown"
            confidence = face_score * 0.7 + liveness_score * 0.3
            is_confident = (name is not None and face_score >= FACE_SIM_THRESHOLD and liveness_score >= LIVENESS_THRESHOLD)
            color = (0, 255, 0) if is_confident else (0, 165, 255)
            
            # Draw biometric frame (FaceID-style brackets)
            draw_biometric_frame(frame, x, y, w, h, color, thickness=2)
            
            # Draw identity badge
            if name:
                draw_identity_badge(frame, x, y, w, h, label)
            
            # Draw confidence meter
            meter_x = x + w // 2
            meter_y = y + h + 60
            draw_confidence_meter(frame, meter_x, meter_y, confidence, radius=28)
            cv2.putText(frame, f"Frame {frames_collected}/{CONSENSUS_FRAMES}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            
            cv2.imshow("Face Attendance System", frame)
            cv2.waitKey(1)  # Process events, don't block
        
        # All 3 frames collected - analyze results
        named_votes = [n for n in names if n != "UNKNOWN"]
        if len(named_votes) < MIN_FRAMES_FOR_DECISION:
            print(f"[-] Face not recognized - insufficient matches ({len(named_votes)}/{MIN_FRAMES_FOR_DECISION})")
            return None, 0, 0, 0
        
        # Get consensus
        from collections import Counter
        vote_counts = Counter(named_votes)
        final_name, vote_count = vote_counts.most_common(1)[0]
        
        # Check if consensus is strong enough
        consensus_score = vote_count / len(names)
        if consensus_score < CONSENSUS_THRESHOLD:
            print(f"[-] No consensus ({consensus_score:.0%} < {CONSENSUS_THRESHOLD:.0%})")
            return None, 0, 0, 0
        
        # Average scores from matching frames only
        matching_indices = [i for i, n in enumerate(names) if n == final_name]
        if not matching_indices:
            return None, 0, 0, 0
        
        avg_face_score = sum(scores[i] for i in matching_indices) / len(matching_indices)
        avg_liveness = sum(lives[i] for i in matching_indices) / len(matching_indices)
        final_confidence = EMB_WEIGHT * avg_face_score + LIVE_WEIGHT * avg_liveness
        
        return final_name, avg_face_score, avg_liveness, final_confidence
    
    def register(self):
        """Register a new user by capturing multiple face samples."""
        name = input("\nEnter user name: ").strip()
        
        if not name:
            print("[-] Invalid name")
            return
        
        if name in self.db:
            overwrite = input(f"User '{name}' exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("✗ Registration cancelled")
                return
        
        print(f"\n-> Registering '{name}'... Look at camera steadily")
        print(f"  Capturing {REG_SAMPLES} samples...")
        
        samples = []
        cv2.namedWindow("Registration", cv2.WINDOW_AUTOSIZE)
        
        while len(samples) < REG_SAMPLES:
            ret, frame = self.cap.read()
            if not ret:
                print("[-] Camera read error")
                cv2.destroyWindow("Registration")
                return
            
            face = detect_face(frame)
            
            # Show frame with sample count
            display = frame.copy()
            if face is not None:
                samples.append(get_embedding(face))
                color = (0, 255, 0)
                status = "DETECTED"
            else:
                color = (0, 0, 255)
                status = "NO FACE"
            
            cv2.putText(
                display,
                f"Samples: {len(samples)}/{REG_SAMPLES}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                color,
                2
            )
            cv2.putText(
                display,
                status,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )
            
            cv2.imshow("Registration", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[-] Registration cancelled")
                cv2.destroyWindow("Registration")
                return
        
        cv2.destroyWindow("Registration")
        
        # Average embeddings
        avg_embedding = np.mean(samples, axis=0)
        self.db[name] = avg_embedding
        save_db(self.db)
        
        print(f"[+] '{name}' registered successfully!")
    
    def attend(self, punch_type):
        """
        Fast consensus verification for punch-in/out.
        Uses only CONSENSUS_FRAMES (3) for ~100ms latency.
        Shows real-time face detection with bounding box.
        
        Args:
            punch_type (str): "Punch-In" or "Punch-Out"
        """
        # Verify identity using consensus voting
        name, face_score, liveness_score, final_confidence = self._verify_for_action(punch_type)
        
        if name is None:
            print("\n" + "="*70)
            print("Status: REJECTED - No valid identity detected")
            print("="*70 + "\n")
            return
        
        # DECISION LOGIC - Check all thresholds
        rejection_reason = None
        
        if face_score < FACE_SIM_THRESHOLD:
            rejection_reason = (REJECTION_LOW_SIM,
                              f"Face similarity {face_score:.3f} < {FACE_SIM_THRESHOLD}")
        elif liveness_score < LIVENESS_THRESHOLD:
            rejection_reason = (REJECTION_LOW_LIVE,
                              f"Liveness {liveness_score:.3f} < {LIVENESS_THRESHOLD}")
        elif final_confidence < FINAL_CONF_THRESHOLD:
            rejection_reason = (REJECTION_LOW_CONF,
                              f"Final confidence {final_confidence:.3f} < {FINAL_CONF_THRESHOLD}")
        
        # Determine status
        if rejection_reason is None:
            status = "ACCEPTED"
            rejection_category = None
        else:
            status = "REJECTED"
            rejection_category, rejection_detail = rejection_reason
        
        # Log attendance
        self._log_attendance(
            name,
            punch_type,
            face_score,
            liveness_score,
            final_confidence,
            status,
            rejection_category if rejection_reason else None
        )
        
        # Display result
        print(f"\n{'='*70}")
        print(f"VERIFICATION RESULT")
        print(f"{'='*70}")
        print(f"Punch Type:        {punch_type}")
        print(f"Identity:          {name}")
        print(f"Face Similarity:   {face_score:.3f} (threshold: {FACE_SIM_THRESHOLD})")
        print(f"Liveness Score:    {liveness_score:.3f} (threshold: {LIVENESS_THRESHOLD})")
        print(f"Final Confidence:  {final_confidence:.3f} (threshold: {FINAL_CONF_THRESHOLD})")
        print(f"Status:            {status}")
        
        if rejection_reason:
            print(f"Reason:            {rejection_reason[0]}")
        
        print(f"{'='*70}\n")
        
        # User feedback
        if status == "ACCEPTED":
            print(f"[+] {punch_type} marked for {name}")
            # FIX #3: Set cooldown after successful punch
            self.last_action_time = time.time()
        else:
            print(f"[-] {punch_type} rejected - {rejection_category}")
    
    def _log_attendance(self, name, punch_type, face_score, liveness_score, 
                        final_confidence, status, rejection_reason=None):
        """
        Log attendance to CSV with single-action prevention.
        
        Args:
            name (str): User name
            punch_type (str): "Punch-In" or "Punch-Out"
            face_score (float): Average face similarity score
            liveness_score (float): Average liveness detection score
            final_confidence (float): Final weighted confidence score
            status (str): "ACCEPTED" or "REJECTED"
            rejection_reason (str): Category of rejection (if applicable)
        """
        # Prevent duplicate punches for same user in quick succession
        # (e.g., multiple punch-ins while standing in front of camera)
        current_time = datetime.now()
        last_key = (name, punch_type)
        
        # Check if punch was logged in last 60 seconds
        if last_key in self.last_attendance:
            time_diff = (current_time - self.last_attendance[last_key]).total_seconds()
            if time_diff < 60 and status == "ACCEPTED":
                print(f"⚠ {punch_type} for {name} already logged {time_diff:.0f}s ago - skipping duplicate")
                return
        
        df = pd.read_csv(ATTENDANCE_CSV)
        
        new_record = {
            "name": name,
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "punch_type": punch_type,
            "face_score": round(face_score, 3),
            "liveness_score": round(liveness_score, 3),
            "final_confidence": round(final_confidence, 3),
            "status": status,
            "rejection_reason": rejection_reason if rejection_reason else ""
        }
        
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(ATTENDANCE_CSV, index=False)
        
        # Update last attendance timestamp
        if status == "ACCEPTED":
            self.last_attendance[last_key] = current_time
    
    def run(self):
        """Main event loop with real-time face detection visualization."""
        print("-> System running. Press keys or close window to interact.\n")
        
        # FIX #2: Skip frames to reduce FaceNet calls
        FRAME_SKIP = 5
        frame_count = 0
        
        # Initialize prediction variables to persist across frames
        name = "Unknown"
        face_sim = 0.0
        live_score = 0.0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("[-] Camera read error")
                    break
                
                frame_count += 1
                
                # FIX #2: Live frame-by-frame prediction with visual feedback
                display_frame = frame.copy()
                
                # Detect face and get bounding box
                face, box = detect_face(frame, return_box=True)
                
                if face is not None and box is not None:
                    x, y, w, h = box
                    
                    # FIX #2: Only run FaceNet every FRAME_SKIP frames (every 5th frame)
                    if frame_count % FRAME_SKIP == 0:
                        # Get real-time prediction
                        emb = get_embedding(face)
                        name, face_sim = recognize_single(emb, self.db)
                        live_score = liveness(face)
                    
                    # Calculate confidence
                    final_confidence = face_sim * 0.7 + live_score * 0.3
                    
                    # Determine if confident
                    is_confident = (name is not None and 
                                   face_sim >= FACE_SIM_THRESHOLD and 
                                   live_score >= LIVENESS_THRESHOLD)
                    
                    # FIX #4: Use professional UI instead of raw text
                    box_color = (0, 255, 0) if is_confident else (0, 165, 255)
                    
                    # FIX #2: Draw biometric frame (FaceID-style brackets)
                    draw_biometric_frame(display_frame, x, y, w, h, box_color, thickness=2)
                    
                    # FIX #5: Draw identity badge
                    identity_text = name if name else "Unknown"
                    draw_identity_badge(display_frame, x, y, w, h, identity_text)
                    
                    # FIX #3: Draw animated scanning line
                    draw_scanning_line(display_frame, x, y, w, h, frame_count, box_color)
                    
                    # FIX #4: Draw confidence meter instead of raw numbers
                    meter_x = x + w // 2
                    meter_y = y + h + 55
                    draw_confidence_meter(display_frame, meter_x, meter_y, final_confidence, radius=28)
                    
                else:
                    # FIX #1: Soft status banner instead of alarming red text
                    draw_status_banner(display_frame, "Searching for face...", "info")
                
                # Draw instructions at bottom
                cv2.putText(display_frame, "Press [R]egister  [I]n  [O]ut  [Q]uit", 
                           (10, display_frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.5, (255, 255, 255), 1)
                
                # Display live feed
                cv2.imshow("Face Attendance System", display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('r') or key == ord('R'):
                    self.register()
                
                elif key == ord('i') or key == ord('I'):
                    # Check cooldown to prevent duplicate punches
                    if time.time() - self.last_action_time >= self.COOLDOWN:
                        self.attend("Punch-In")
                    else:
                        print(f"⏳ Please wait {self.COOLDOWN - (time.time() - self.last_action_time):.1f}s before next punch")
                
                elif key == ord('o') or key == ord('O'):
                    # Check cooldown to prevent duplicate punches
                    if time.time() - self.last_action_time >= self.COOLDOWN:
                        self.attend("Punch-Out")
                    else:
                        print(f"⏳ Please wait {self.COOLDOWN - (time.time() - self.last_action_time):.1f}s before next punch")
                
                elif key == ord('q') or key == ord('Q'):
                    print("\n[+] System shutdown initiated...")
                    break
        
        except KeyboardInterrupt:
            print("\n[-] Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        print("[+] All resources released")
        print("[+] Goodbye!\n")


def main():
    """Entry point."""
    try:
        system = FaceAttendanceSystem()
        system.run()
    except Exception as e:
        print(f"\n[-] Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
