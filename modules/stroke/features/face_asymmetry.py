"""
StrokeAI - NetLag HUD + Face Asymmetry (absolute paths + guaranteed CSV)
Keys:
  r = start/stop recording (auto-saves CSV on stop)
  c = force-save CSV anytime
  s = save averaged JSON
  q = quit
"""

import cv2, mediapipe as mp, numpy as np, uuid, os, csv, time, json
from datetime import datetime
from pathlib import Path

# ---------- Absolute Paths ----------
ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "data" / "logs"
EXP_DIR = ROOT / "data" / "exports"
LOG_DIR.mkdir(parents=True, exist_ok=True)
EXP_DIR.mkdir(parents=True, exist_ok=True)

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Symmetric landmark pairs
PAIRS = [(61, 291), (133, 362), (33, 263)]
L_EYE_OUT, R_EYE_OUT = 33, 263


def _pt(landmarks, idx, w, h):
    lm = landmarks[idx]
    return np.array([lm.x * w, lm.y * h], dtype=np.float32)


def compute_asymmetry_from_landmarks(landmarks, image_shape):
    h, w = image_shape[:2]
    eps = 1e-6
    try:
        iod = np.linalg.norm(
            _pt(landmarks, R_EYE_OUT, w, h) - _pt(landmarks, L_EYE_OUT, w, h)
        ) + eps
    except Exception:
        return 1.0, {"error": "incomplete landmarks"}

    l_eye_ref = _pt(landmarks, L_EYE_OUT, w, h)
    r_eye_ref = _pt(landmarks, R_EYE_OUT, w, h)

    diffs = []
    for L_idx, R_idx in PAIRS:
        try:
            Lp = _pt(landmarks, L_idx, w, h)
            Rp = _pt(landmarks, R_idx, w, h)
            L_vert = abs(Lp[1] - l_eye_ref[1]) / iod
            R_vert = abs(Rp[1] - r_eye_ref[1]) / iod
            diffs.append(abs(L_vert - R_vert))
        except Exception:
            continue

    ai = float(np.mean(diffs)) if diffs else 1.0
    return ai, {"pairs": len(diffs), "inter_ocular": float(iod)}


def _save_csv(ai_log):
    """Write ai_log to CSV (absolute path). ai_log = [(t_abs, ai_or_nan), ...]"""
    if not ai_log:
        print("⚠️ Empty log, not writing CSV.")
        return None

    csv_path = LOG_DIR / f"face_ai_session_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    base_t = ai_log[0][0]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["t_sec", "ai"])
        for t_abs, ai in ai_log:
            w.writerow([t_abs - base_t, "" if np.isnan(ai) else ai])

    print(f"✅ Saved CSV → {csv_path}")
    return csv_path


def _save_avg_json(ai_log):
    valid = [v for _, v in ai_log if not np.isnan(v)]
    if not valid:
        print("⚠️ No valid AI samples to average.")
        return None

    avg_ai = float(np.mean(valid))
    record = {
        "id": str(uuid.uuid4()),
        "module": "stroke",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "signals": {"face_asymmetry_avg": avg_ai, "samples": len(valid)},
        "device": "webcam",
        "notes": "live capture average",
    }

    json_path = EXP_DIR / "neuro_unit_face_ai_avg.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"✅ Saved averaged AI JSON → {json_path}")
    return json_path


def run_webcam():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("📷 Keys: r=start/stop CSV, c=force-save CSV, s=save avg JSON, q=quit")

    recording = False
    ai_log = []
    start_time = None
    last_time = time.time()
    fps = 0.0

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("⚠️ cap.read() failed")
                break

            # FPS (EWMA)
            now = time.time()
            dt = now - last_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)
            last_time = now

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            current_ai = np.nan
            if results.multi_face_landmarks:
                fl = results.multi_face_landmarks[0]
                mp_drawing.draw_landmarks(
                    frame,
                    fl,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        thickness=1, circle_radius=1
                    ),
                )
                ai, _ = compute_asymmetry_from_landmarks(fl.landmark, frame.shape)
                current_ai = float(ai)
                cv2.putText(
                    frame,
                    f"AI: {current_ai:.3f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    frame,
                    "Face not detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            # HUD overlay
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2,
            )

            if recording:
                cv2.putText(
                    frame,
                    "REC ●",
                    (540, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )
                ai_log.append((time.time(), current_ai))

            cv2.imshow("StrokeAI - NetLag HUD", frame)
            key = cv2.waitKey(1) & 0xFF

            # --- Keys ---
            if key == ord("r"):
                if not recording:
                    ai_log = []
                    start_time = time.time()
                    recording = True
                    print("🎥 Recording started...")
                else:
                    recording = False
                    duration = time.time() - start_time
                    print(
                        f"🛑 Recording stopped. {len(ai_log)} samples, {duration:.1f}s"
                    )
                    _save_csv(ai_log)  # ✅ auto-save CSV when stopped

            elif key == ord("c"):
                if ai_log:
                    _save_csv(ai_log)
                else:
                    print("⚠️ No samples yet to save.")

            elif key == ord("s"):
                _save_avg_json(ai_log)

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("🔵 ROOT =", ROOT)
    print("🔵 LOG_DIR =", LOG_DIR)
    print("🔵 EXP_DIR =", EXP_DIR)
    run_webcam()
