# modules/stroke/features/face_asymmetry.py
# Live face-landmark viewer + facial asymmetry index (AI)
# Keys: r = start/stop CSV logging, s = save JSON summary, q = quit

from datetime import datetime
import uuid, os, json, time
import cv2
import mediapipe as mp
import numpy as np

# ------------------ Asymmetry computation ------------------
# MediaPipe FaceMesh indices:
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
    """Robust asymmetry index using multiple symmetric pairs."""
    h, w = image_shape[:2]
    eps = 1e-6
    iod = np.linalg.norm(_pt(landmarks, R_EYE_OUT, w, h) - _pt(landmarks, L_EYE_OUT, w, h)) + eps
    l_eye_ref = _pt(landmarks, L_EYE_OUT, w, h)
    r_eye_ref = _pt(landmarks, R_EYE_OUT, w, h)

    Ls, Rs, diffs = [], [], []
    for L_idx, R_idx in PAIRS:
        Lp = _pt(landmarks, L_idx, w, h)
        Rp = _pt(landmarks, R_idx, w, h)
        L_vert = abs(Lp[1] - l_eye_ref[1]) / iod
        R_vert = abs(Rp[1] - r_eye_ref[1]) / iod
        Ls.append(L_vert); Rs.append(R_vert); diffs.append(abs(L_vert - R_vert))

    Ls, Rs = np.array(Ls, dtype=np.float32), np.array(Rs, dtype=np.float32)
    ai = float(np.mean(diffs) / (np.mean(Ls + Rs) + eps))
    return ai, {"L_avg": float(np.mean(Ls)), "R_avg": float(np.mean(Rs)), "inter_ocular_norm": float(iod)}

# ------------------ ONF saver (optional) ------------------
try:
    from onf.sdk.io import save_neuro_unit
except Exception:
    save_neuro_unit = None

# ------------------ Public API: run_webcam ------------------
def run_webcam(save_path="data/exports/neuro_unit_face_ai_avg.json"):
    """Open webcam, display landmarks + AI, log CSV on r…r, save JSON on s."""
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh

    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)

    print("[StrokeAI] Opening webcam…")
    cv2.namedWindow("StrokeAI – Face Asymmetry", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("StrokeAI – Face Asymmetry", 960, 540)

    # Use the same backend that worked for you: try DSHOW then MSMF
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[StrokeAI] ⚠️ DSHOW failed; trying MSMF…")
        cap.release()
        cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

    if not cap.isOpened():
        print("[StrokeAI] ❌ Could not open webcam on idx=0 (DSHOW or MSMF).")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("[StrokeAI] ✅ Webcam opened. Press r=start/stop, s=save JSON, q=quit.")

    recording = False
    ai_log = []          # list of (t_sec, ai)
    start_time = None
    last_ai = None

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:
            ok, frame = cap.read()
            if not ok or frame is None or frame.size == 0:
                print("[StrokeAI] ⚠️ Frame read failed. Is the camera in use?")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                fl = results.multi_face_landmarks[0]
                mp_drawing.draw_landmarks(
                    frame, fl, mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
                )
                ai, _details = compute_asymmetry_from_landmarks(fl.landmark, frame.shape)
                last_ai = ai
                if recording:
                    ai_log.append((time.time() - start_time, float(ai)))
                cv2.putText(frame, f"AI: {ai:.3f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            else:
                cv2.putText(frame, "Face not detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

            if recording:
                cv2.putText(frame, "REC", (550, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

            cv2.imshow("StrokeAI – Face Asymmetry", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('r'):
                if not recording:
                    ai_log.clear()
                    start_time = time.time()
                    recording = True
                    print("🎥 Recording started…")
                else:
                    recording = False
                    duration = time.time() - start_time
                    # write CSV
                    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    csv_path = f"data/logs/face_ai_session_{stamp}.csv"
                    import csv
                    with open(csv_path, "w", newline="", encoding="utf-8") as f:
                        w = csv.writer(f)
                        w.writerow(["t_sec","ai"])
                        w.writerows(ai_log)
                    print(f"🛑 Recording stopped. {len(ai_log)} samples, {duration:.1f}s")
                    print(f"✅ Saved CSV log → {csv_path}")

            elif key == ord('s'):
                if last_ai is None and not ai_log:
                    print("⚠️ Nothing to save yet.")
                else:
                    avg_ai = float(np.mean([v for _,v in ai_log])) if ai_log else float(last_ai)
                    duration = (time.time() - start_time) if start_time else 0.0
                    record = {
                        "id": str(uuid.uuid4()),
                        "module": "stroke",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "signals": {
                            "face_asymmetry_avg": avg_ai,
                            "samples": len(ai_log),
                            "duration_sec": float(duration),
                        },
                        "device": "webcam",
                        "notes": "AI average session"
                    }
                    if save_neuro_unit:
                        out = save_neuro_unit(record, path=save_path)
                        print(f"✅ Saved averaged AI JSON → {out}")
                    else:
                        with open(save_path, "w", encoding="utf-8") as f:
                            json.dump(record, f, indent=2)
                        print(f"✅ Saved averaged AI JSON → {save_path}")

            elif key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# ------------------ CLI entry ------------------
if __name__ == "__main__":
    print("Launching StrokeAI webcam…")
    run_webcam()
