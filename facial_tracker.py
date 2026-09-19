# ============================================================
# facial_tracker.py — Complete Behavioural Tracking Module
# Compatible with Python 3.13 + MediaPipe 0.10.9
# ============================================================
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'

import warnings
warnings.filterwarnings('ignore')

# Fix NumPy compatibility
try:
    import numpy as np
    # Test if cv2 will work
    import cv2
except Exception:
    pass
import cv2
import numpy as np
import time

# ============================================================
# SAFE MEDIAPIPE IMPORT
# ============================================================
MEDIAPIPE_OK = False
mp_face_mesh = None
mp_drawing   = None

try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing   = mp.solutions.drawing_utils
    MEDIAPIPE_OK = True
    print("MediaPipe loaded successfully!")
except Exception as e:
    print(f"MediaPipe not available: {e}")
    print("Running in basic OpenCV mode.")

# ============================================================
# EYE LANDMARK INDICES (MediaPipe FaceMesh 468 points)
# ============================================================
LEFT_EYE_TOP     = 159
LEFT_EYE_BOTTOM  = 145
LEFT_EYE_LEFT    = 33
LEFT_EYE_RIGHT   = 133
RIGHT_EYE_TOP    = 386
RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_LEFT   = 362
RIGHT_EYE_RIGHT  = 263
NOSE_TIP         = 1

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def eye_aspect_ratio(landmarks, top_idx, bottom_idx,
                     left_idx, right_idx, w, h):
    """
    Eye Aspect Ratio (EAR) formula for blink detection.
    EAR = vertical eye height / horizontal eye width
    Open eye  -> EAR ~0.3
    Closed eye -> EAR ~0.0
    """
    top    = landmarks[top_idx]
    bottom = landmarks[bottom_idx]
    left   = landmarks[left_idx]
    right  = landmarks[right_idx]

    top_pt    = np.array([top.x * w,    top.y * h])
    bottom_pt = np.array([bottom.x * w, bottom.y * h])
    left_pt   = np.array([left.x * w,   left.y * h])
    right_pt  = np.array([right.x * w,  right.y * h])

    vertical   = np.linalg.norm(top_pt - bottom_pt)
    horizontal = np.linalg.norm(left_pt - right_pt)

    if horizontal == 0:
        return 0.0
    return float(vertical / horizontal)


def get_gaze_score(landmarks):
    """
    Gaze score based on nose tip horizontal position.
    0.5 = center = good eye contact = score 1.0
    Far from center = looking away = lower score
    """
    nose_x           = landmarks[NOSE_TIP].x
    dist_from_center = abs(nose_x - 0.5)
    return float(max(0.0, 1.0 - dist_from_center * 4.0))


def calculate_final_scores(blink_count, elapsed, gaze_scores,
                           head_positions, ear_values,
                           frames_with_face, total_frames):
    """
    Calculate all behavioral scores from raw tracking data.
    Returns a complete results dictionary.
    """
    # 1. Face presence (how often face was visible)
    face_presence = (frames_with_face / max(total_frames, 1)) * 100.0

    # 2. Eye contact score
    avg_gaze = float(np.mean(gaze_scores) * 100) if gaze_scores else 0.0

    # 3. Blink rate (blinks per minute)
    minutes        = max(elapsed, 1.0) / 60.0
    blinks_per_min = blink_count / minutes

    # Normal blink rate = 12-22 per minute
    if 12 <= blinks_per_min <= 22:
        blink_score = 100.0
    elif blinks_per_min < 12:
        blink_score = max(0.0, (blinks_per_min / 12.0) * 100.0)
    else:
        blink_score = max(0.0, 100.0 - (blinks_per_min - 22.0) * 5.0)

    # 4. Head movement stability
    if len(head_positions) > 1:
        pos_array  = np.array(head_positions)
        movement   = float(np.std(pos_array[:, 0]) + np.std(pos_array[:, 1]))
        head_score = float(max(0.0, min(100.0, (1.0 - movement / 0.05) * 100.0)))
    else:
        head_score = 50.0

    # 5. Expression variability (via EAR standard deviation)
    if len(ear_values) > 1:
        ear_std          = float(np.std(ear_values))
        expression_score = float(min(100.0, ear_std * 1000.0))
    else:
        expression_score = 50.0

    # 6. Weighted combined behavioral score
    # Eye contact weighted highest as strongest ASD indicator
    behavioral_score = (
        avg_gaze         * 0.35 +
        blink_score      * 0.25 +
        head_score       * 0.15 +
        face_presence    * 0.15 +
        expression_score * 0.10
    )

    # 7. Risk classification
    if behavioral_score >= 70:
        behavioral_risk = "Low Behavioral Risk"
        risk_color      = "green"
    elif behavioral_score >= 45:
        behavioral_risk = "Moderate Behavioral Risk"
        risk_color      = "orange"
    else:
        behavioral_risk = "High Behavioral Risk"
        risk_color      = "red"

    return {
        "behavioral_score":  round(behavioral_score, 2),
        "behavioral_risk":   behavioral_risk,
        "risk_color":        risk_color,
        "eye_contact":       round(avg_gaze, 2),
        "blink_rate":        round(blinks_per_min, 2),
        "blink_score":       round(blink_score, 2),
        "head_movement":     round(head_score, 2),
        "face_presence":     round(face_presence, 2),
        "expression_score":  round(expression_score, 2),
        "duration_seconds":  round(elapsed, 1),
        "total_frames":      total_frames,
        "frames_with_face":  frames_with_face,
    }


# ============================================================
# FULL MEDIAPIPE TRACKER
# ============================================================

def run_with_mediapipe(duration=30):
    """
    Full facial tracking using MediaPipe FaceMesh.
    Tracks 468 facial landmarks for precise measurements.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"error": "Could not open webcam. Check camera permissions."}

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Tracking variables
    blink_count      = 0
    blink_cooldown   = 0
    frames_with_face = 0
    total_frames     = 0
    gaze_scores      = []
    head_positions   = []
    ear_values       = []
    EAR_THRESHOLD    = 0.20
    BLINK_COOLDOWN   = 3
    elapsed          = 0.0
    start_time       = time.time()

    try:
        face_mesh_obj = mp_face_mesh.FaceMesh(
            max_num_faces          = 1,
            refine_landmarks       = True,
            min_detection_confidence = 0.5,
            min_tracking_confidence  = 0.5
        )
    except Exception as e:
        cap.release()
        return {"error": f"FaceMesh initialization failed: {str(e)}"}

    with face_mesh_obj as face_mesh:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1
            h, w          = frame.shape[:2]
            frame         = cv2.flip(frame, 1)
            rgb           = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results       = face_mesh.process(rgb)
            rgb.flags.writeable = True

            # UI overlay
            remaining = int(duration - elapsed)
            cv2.rectangle(frame, (0, 0), (w, 50), (15, 15, 26), -1)
            cv2.putText(frame,
                       f"AutismAI Face Analysis  |  {remaining}s remaining",
                       (10, 33), cv2.FONT_HERSHEY_SIMPLEX,
                       0.65, (167, 139, 250), 2)

            if results.multi_face_landmarks:
                frames_with_face += 1
                lms = results.multi_face_landmarks[0].landmark

                # EAR
                l_ear = eye_aspect_ratio(lms, LEFT_EYE_TOP, LEFT_EYE_BOTTOM,
                                         LEFT_EYE_LEFT, LEFT_EYE_RIGHT, w, h)
                r_ear = eye_aspect_ratio(lms, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM,
                                         RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT, w, h)
                avg_ear = (l_ear + r_ear) / 2.0
                ear_values.append(avg_ear)

                # Blink detection
                if avg_ear < EAR_THRESHOLD and blink_cooldown == 0:
                    blink_count   += 1
                    blink_cooldown = BLINK_COOLDOWN
                if blink_cooldown > 0:
                    blink_cooldown -= 1

                # Gaze
                gaze = get_gaze_score(lms)
                gaze_scores.append(gaze)

                # Head position
                nose = lms[NOSE_TIP]
                head_positions.append((nose.x, nose.y))

                # Draw landmarks as dots
                for lm in lms:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    cv2.circle(frame, (px, py), 1, (124, 58, 237), -1)

                # Live stats overlay
                cv2.rectangle(frame, (0, h-110), (220, h), (15, 15, 26), -1)
                cv2.putText(frame, f"EAR    : {avg_ear:.3f}",
                           (10, h-85), cv2.FONT_HERSHEY_SIMPLEX,
                           0.55, (100, 255, 150), 1)
                cv2.putText(frame, f"Blinks : {blink_count}",
                           (10, h-60), cv2.FONT_HERSHEY_SIMPLEX,
                           0.55, (100, 255, 150), 1)
                cv2.putText(frame, f"Gaze   : {gaze:.2f}",
                           (10, h-35), cv2.FONT_HERSHEY_SIMPLEX,
                           0.55, (100, 255, 150), 1)
                cv2.putText(frame, f"Face   : YES",
                           (10, h-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.55, (100, 255, 150), 1)

            else:
                cv2.rectangle(frame, (0, h-40), (260, h), (15, 15, 26), -1)
                cv2.putText(frame,
                           "No face detected — move closer or improve lighting",
                           (10, h-15), cv2.FONT_HERSHEY_SIMPLEX,
                           0.5, (0, 100, 255), 1)

            # Progress bar at bottom
            progress = int((elapsed / duration) * w)
            cv2.rectangle(frame, (0, h-3), (w, h), (30, 30, 60), -1)
            cv2.rectangle(frame, (0, h-3), (progress, h), (124, 58, 237), -1)

            cv2.imshow("AutismAI — Facial Behaviour Analysis", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    return calculate_final_scores(
        blink_count, elapsed, gaze_scores,
        head_positions, ear_values,
        frames_with_face, total_frames
    )


# ============================================================
# BASIC OPENCV TRACKER (fallback when MediaPipe unavailable)
# ============================================================

def run_with_opencv_only(duration=30):
    """
    Fallback tracker using OpenCV Haar cascade face detection.
    Less precise but works without MediaPipe.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"error": "Could not open webcam. Check camera permissions."}

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml'
    )

    frames_with_face = 0
    total_frames     = 0
    eye_contact_list = []
    head_positions   = []
    blink_count      = 0
    prev_eyes        = 0
    elapsed          = 0.0
    start_time       = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break

        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1
        h, w  = frame.shape[:2]
        frame = cv2.flip(frame, 1)
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # UI overlay
        remaining = int(duration - elapsed)
        cv2.rectangle(frame, (0, 0), (w, 50), (15, 15, 26), -1)
        cv2.putText(frame,
                   f"AutismAI Face Analysis  |  {remaining}s remaining",
                   (10, 33), cv2.FONT_HERSHEY_SIMPLEX,
                   0.65, (167, 139, 250), 2)

        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        if len(faces) > 0:
            frames_with_face += 1
            x, y, fw, fh = faces[0]

            # Face center as gaze proxy
            cx = (x + fw / 2) / w
            cy = (y + fh / 2) / h
            head_positions.append((cx, cy))

            # Gaze score
            dist_from_center = abs(cx - 0.5)
            gaze_score       = max(0.0, 1.0 - dist_from_center * 4.0)
            eye_contact_list.append(gaze_score)

            # Eye detection for blink count
            roi_gray = gray[y:y+fh, x:x+fw]
            eyes     = eye_cascade.detectMultiScale(roi_gray)
            curr_eyes = len(eyes)

            # Blink = eyes disappeared and reappeared
            if prev_eyes >= 2 and curr_eyes == 0:
                blink_count += 1
            prev_eyes = curr_eyes

            # Draw face box
            cv2.rectangle(frame, (x, y), (x+fw, y+fh), (124, 58, 237), 2)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame,
                             (x+ex, y+ey),
                             (x+ex+ew, y+ey+eh),
                             (100, 255, 150), 1)

            # Stats overlay
            cv2.rectangle(frame, (0, h-90), (220, h), (15, 15, 26), -1)
            cv2.putText(frame, f"Blinks : {blink_count}",
                       (10, h-65), cv2.FONT_HERSHEY_SIMPLEX,
                       0.55, (100, 255, 150), 1)
            cv2.putText(frame, f"Gaze   : {gaze_score:.2f}",
                       (10, h-40), cv2.FONT_HERSHEY_SIMPLEX,
                       0.55, (100, 255, 150), 1)
            cv2.putText(frame, f"Face   : YES",
                       (10, h-15), cv2.FONT_HERSHEY_SIMPLEX,
                       0.55, (100, 255, 150), 1)
        else:
            cv2.rectangle(frame, (0, h-40), (260, h), (15, 15, 26), -1)
            cv2.putText(frame,
                       "No face detected — move closer",
                       (10, h-15), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 100, 255), 1)

        # Progress bar
        progress = int((elapsed / duration) * w)
        cv2.rectangle(frame, (0, h-3), (w, h), (30, 30, 60), -1)
        cv2.rectangle(frame, (0, h-3), (progress, h), (124, 58, 237), -1)

        cv2.imshow("AutismAI — Facial Behaviour Analysis", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Calculate scores from basic tracking data
    face_presence  = (frames_with_face / max(total_frames, 1)) * 100.0
    avg_gaze       = float(np.mean(eye_contact_list) * 100) \
                     if eye_contact_list else 0.0
    minutes        = max(elapsed, 1.0) / 60.0
    blinks_per_min = blink_count / minutes

    if 12 <= blinks_per_min <= 22:
        blink_score = 100.0
    elif blinks_per_min < 12:
        blink_score = max(0.0, (blinks_per_min / 12.0) * 100.0)
    else:
        blink_score = max(0.0, 100.0 - (blinks_per_min - 22.0) * 5.0)

    if len(head_positions) > 1:
        pos_array  = np.array(head_positions)
        movement   = float(np.std(pos_array[:, 0]) + np.std(pos_array[:, 1]))
        head_score = float(max(0.0, min(100.0,
                          (1.0 - movement / 0.05) * 100.0)))
    else:
        head_score = 50.0

    behavioral_score = (
        avg_gaze      * 0.35 +
        blink_score   * 0.25 +
        head_score    * 0.15 +
        face_presence * 0.15 +
        50.0          * 0.10
    )

    if behavioral_score >= 70:
        behavioral_risk = "Low Behavioral Risk"
        risk_color      = "green"
    elif behavioral_score >= 45:
        behavioral_risk = "Moderate Behavioral Risk"
        risk_color      = "orange"
    else:
        behavioral_risk = "High Behavioral Risk"
        risk_color      = "red"

    return {
        "behavioral_score":  round(behavioral_score, 2),
        "behavioral_risk":   behavioral_risk,
        "risk_color":        risk_color,
        "eye_contact":       round(avg_gaze, 2),
        "blink_rate":        round(blinks_per_min, 2),
        "blink_score":       round(blink_score, 2),
        "head_movement":     round(head_score, 2),
        "face_presence":     round(face_presence, 2),
        "expression_score":  50.0,
        "duration_seconds":  round(elapsed, 1),
        "total_frames":      total_frames,
        "frames_with_face":  frames_with_face,
        "mode":              "basic"
    }


# ============================================================
# PUBLIC FUNCTION — called by app.py
# ============================================================

def run_facial_tracking(duration=30):
    """
    Automatically picks best available tracking method.
    Uses full MediaPipe if available, falls back to OpenCV.
    """
    if MEDIAPIPE_OK:
        print("Starting full MediaPipe tracking...")
        result = run_with_mediapipe(duration)
        result["mode"] = "full"
        return result
    else:
        print("Starting basic OpenCV tracking...")
        return run_with_opencv_only(duration)


# ============================================================
# TEST — run this file directly to test
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  AutismAI Facial Tracker — Standalone Test")
    print("=" * 50)
    print(f"MediaPipe available: {MEDIAPIPE_OK}")
    print("Starting 15 second test...")
    print("Press Q on the webcam window to quit early")
    print()

    results = run_facial_tracking(duration=15)

    print("\n" + "=" * 50)
    print("  RESULTS")
    print("=" * 50)
    for key, value in results.items():
        print(f"  {key:25s}: {value}")