# modules/stroke/features/face_asymmetry.py
# Live face-landmark viewer + simple facial asymmetry index (AI)
# Press 's' to save current AI as a Neuro Unit JSON; press 'q' to quit.

from datetime import datetime
import uuid
import cv2
import mediapipe as mp
import numpy as np

try:
    # Optional: save to Neuro Unit JSON if the ONF SDK is present
    from onf.sdk.io import save_neuro_unit
except Exception:
    save_neuro_unit = None

# FaceMesh landmark indices we use (MediaPipe):
# Left eye outer corner: 33
# Right eye outer corner: 263
# Left mouth corner: 61
# Right mouth corner: 291
L_EYE = 33
R_EYE = 263
L_MOUTH = 61
R_MOUTH = 291

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

def _landmark_xy(landmarks, idx, img_w, img_h):
    lm = landmarks[idx]
    return np.array([lm.x * img_w, lm.y * img_h], dtype=np.float32)

# ---- Multi-pair asymmetry (replacement) ----
import numpy as np

# MediaPipe FaceMesh indices:
# outer eye corners (for scale), inner eye corners, mouth corners
L_EYE_OUT, R_EYE_OUT = 33, 263
PAIRS = [
    (61, 291),   # mouth corners (L, R)
    (133, 362),  # inner eye corners (L, R)
    (33, 263),   # outer eye corners (L, R)
]

def _pt(landmarks, idx, w, h):
    lm = landmarks[idx]
    return np.array([lm.x * w, lm.y * h], dtype=np.float32)

def compute_asymmetry_from_landmarks(landmarks, image_shape):
    """
    Robust asymmetry index using multiple symmetric pairs.

    Steps:
      1) Normalize vertical distances by inter-ocular distance (outer eye corners).
      2) For each symmetric pair, compute L_vert and R_vert relative to the eye on that side.
      3) AI = mean(|L - R|) / (mean(L + R) + eps), lower = more symmetric.

    Returns:
      ai (float), details (dict)
    """
    h, w = image_shape[:2]
    eps = 1e-6

    # scale: inter-ocular distance
    iod = np.linalg.norm(_pt(landmarks, R_EYE_OUT, w, h) - _pt(landmarks, L_EYE_OUT, w, h)) + eps

    # reference points (per side)
    l_eye_ref = _pt(landmarks, L_EYE_OUT, w, h)
    r_eye_ref = _pt(landmarks, R_EYE_OUT, w, h)

    Ls, Rs, diffs = [], [], []

    for L_idx, R_idx in PAIRS:
        Lp = _pt(landmarks, L_idx, w, h)
        Rp = _pt(landmarks, R_idx, w, h)

        # vertical distances (y) from each side’s reference eye point, normalized
        L_vert = abs(Lp[1] - l_eye_ref[1]) / iod
        R_vert = abs(Rp[1] - r_eye_ref[1]) / iod

        Ls.append(L_vert)
        Rs.append(R_vert)
        diffs.append(abs(L_vert - R_vert))

    Ls = np.array(Ls, dtype=np.float32)
    Rs = np.array(Rs, dtype=np.float32)

    num = float(np.mean(diffs))
    den = float(np.mean(Ls + Rs)) + eps
    ai = num / den

    details = {
        "pairs": PAIRS,
        "L_avg": float(np.mean(Ls)),
        "R_avg": float(np.mean(Rs)),
        "inter_ocular_norm": float(iod),
    }
    return float(ai), details
# ---- end replacement ----

def run_webcam(save_path="data/exports/neuro_unit_face_ai.json"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        print("📷 Running. Press 's' to save current AI, 'q' to quit.")
        last_ai = None

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                fl = results.multi_face_landmarks[0]
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame, fl, mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
                )

                # Compute AI
                ai, details = compute_asymmetry_from_landmarks(
                    fl.landmark, frame.shape
                )
                last_ai = ai

                # Overlay AI
                cv2.putText(
                    frame, f"AI: {ai:.3f} (lower is more symmetric)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                )
            else:
                cv2.putText(
                    frame, "Face not detected",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2
                )

            cv2.imshow("Face Asymmetry (MediaPipe)", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                if last_ai is None:
                    print("⚠️ No AI to save yet.")
                else:
                    record = {
                        "id": str(uuid.uuid4()),
                        "module": "stroke",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "signals": {"face_asymmetry": float(last_ai)},
                        "device": "webcam",
                        "notes": "live capture"
                    }
                    if save_neuro_unit is not None:
                        path = save_neuro_unit(record, path=save_path)
                        print(f"✅ Saved Neuro Unit: {path}")
                    else:
                        # Fallback: save directly if SDK not available
                        import json, os
                        os.makedirs("data/exports", exist_ok=True)
                        with open(save_path, "w", encoding="utf-8") as f:
                            json.dump(record, f, indent=2)
                        print(f"✅ Saved Neuro Unit (fallback): {save_path}")

            if key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam()
