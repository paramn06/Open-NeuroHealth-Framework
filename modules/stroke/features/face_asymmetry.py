"""
StrokeAI - NetLag HUD + Face Asymmetry (absolute paths + guaranteed CSV)
Keys:
  r = start/stop recording (auto-saves CSV on stop)
  c = force-save CSV anytime
  s = save averaged JSON
  q = quit
"""

from __future__ import annotations
import cv2, numpy as np, uuid, os, csv, time, json, math
from datetime import datetime
from pathlib import Path
from typing import Tuple

# ---------- Absolute Paths ----------
ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "data" / "logs"
EXP_DIR = ROOT / "data" / "exports"
LOG_DIR.mkdir(parents=True, exist_ok=True)
EXP_DIR.mkdir(parents=True, exist_ok=True)

# ---------- MediaPipe ----------
# ---- Robust MediaPipe import (works across wheels & avoids top-level crash)
try:
    import mediapipe as mp
    # Import submodules robustly: prefer explicit submodule import to avoid type-checker / attribute errors,
    # but fall back to getattr on the top-level module at runtime if explicit import fails.
    try:
        from mediapipe import solutions as _mp_solutions
        # Prefer an explicit import from the concrete python package so static type checkers
        # (and IDEs) recognize the drawing_utils symbol; fall back to getattr if that fails.
        try:
            from mediapipe.python.solutions import drawing_utils as _mp_drawing
            mp_drawing = _mp_drawing
        except Exception:
            mp_drawing = getattr(_mp_solutions, "drawing_utils", None)
        # Access face_mesh via getattr to avoid static typing issues
        mp_face_mesh = getattr(_mp_solutions, "face_mesh")
    except Exception:
        # Fallback: try to access via the top-level module using getattr to avoid hard attribute errors
        try:
            mp_drawing = getattr(mp.solutions, "drawing_utils")
            mp_face_mesh = getattr(mp.solutions, "face_mesh")
        except Exception:
            raise
except Exception as e:
    raise RuntimeError(
        "⚠️ Mediapipe is not available or failed to load. "
        "Run: conda activate open-neurohealth && pip install mediapipe==0.10.14"
    ) from e


# Symmetric landmark pairs (left_idx, right_idx)
PAIRS = [(61, 291), (133, 362), (33, 263)]
L_EYE_OUT, R_EYE_OUT = 33, 263


# ---------- Helpers ----------
def _pt_nan(landmarks, idx: int, w: int, h: int) -> Tuple[float, float]:
    """Return (x,y) in pixels; returns (nan, nan) if unavailable."""
    try:
        lm = landmarks[idx]
        return float(lm.x * w), float(lm.y * h)
    except Exception:
        return float("nan"), float("nan")

def _mean_ignore_nan(vals) -> float:
    clean = [float(v) for v in vals if not (isinstance(v, float) and math.isnan(v))]
    return float(np.mean(clean)) if clean else float("nan")


# ---------- Core Computation ----------
def compute_asymmetry_from_landmarks(landmarks, image_shape):
    """Compute normalized facial asymmetry index."""
    h, w = image_shape[:2]
    eps = 1e-6

    # Inter-ocular distance (IOD)
    lx, ly = _pt_nan(landmarks, L_EYE_OUT, w, h)
    rx, ry = _pt_nan(landmarks, R_EYE_OUT, w, h)

    if math.isnan(lx) or math.isnan(ly) or math.isnan(rx) or math.isnan(ry):
        return 1.0, {"error": "incomplete landmarks (eyes)"}

    iod = float(math.hypot(rx - lx, ry - ly)) + eps
    l_eye_ref_y = ly
    r_eye_ref_y = ry

    diffs = []
    for L_idx, R_idx in PAIRS:
        _Lx, Ly = _pt_nan(landmarks, L_idx, w, h)
        _Rx, Ry = _pt_nan(landmarks, R_idx, w, h)

        # Only calculate if both points are valid
        if not (math.isnan(Ly) or math.isnan(Ry)):
            L_vert = abs(float(Ly) - float(l_eye_ref_y)) / iod
            R_vert = abs(float(Ry) - float(r_eye_ref_y)) / iod
            diffs.append(abs(L_vert - R_vert))

    ai = _mean_ignore_nan(diffs)
    if math.isnan(ai):
        ai = 1.0

    return float(ai), {"pairs": len(PAIRS), "inter_ocular": float(iod)}


# ---------- CSV / JSON Save ----------
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
            w.writerow([t_abs - base_t, "" if (ai is None or (isinstance(ai, float) and np.isnan(ai))) else ai])

    print(f"[OK] Saved CSV -> {csv_path}")
    return csv_path


def _save_avg_json(ai_log):
    valid = [float(v) for _, v in ai_log if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not valid:
        print("⚠️ No valid AI samples to average.")
        return None

    avg_ai = float(np.mean(valid))
    # --- Quality checks ---
    sample_count = len(valid)
    ai_std = float(np.std(valid))
    if sample_count < 60:
        print(f"⚠️ Warning: Only {sample_count} samples — low data duration, may be unreliable.")
    if ai_std < 1e-6:
        print(f"⚠️ Warning: AI variance too low ({ai_std:.8f}) — face not tracked consistently.")

    record = {
        "id": str(uuid.uuid4()),
        "module": "stroke",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "signals": {"face_asymmetry_avg": avg_ai, "samples": sample_count},
        "device": "webcam",
        "notes": "live capture average",
    }

    json_path = EXP_DIR / "neuro_unit_face_ai_avg.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"[OK] Saved averaged AI JSON -> {json_path}")
    return json_path


# ---------- Webcam / UI ----------
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

            current_ai = float("nan")
            if results.multi_face_landmarks:
                fl = results.multi_face_landmarks[0]
                if mp_drawing is not None and hasattr(mp_drawing, "draw_landmarks"):
                    mp_drawing.draw_landmarks(
                        frame,
                        fl,
                        mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(thickness=1, circle_radius=1),
                    )
                else:
                    # Fallback: draw small circles for each landmark using OpenCV if mediapipe drawing is unavailable
                    h, w = frame.shape[:2]
                    try:
                        for lm in fl.landmark:
                            x = int(lm.x * w)
                            y = int(lm.y * h)
                            if 0 <= x < w and 0 <= y < h:
                                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                    except Exception:
                        # If any unexpected structure occurs, skip fallback drawing
                        pass
                ai, _ = compute_asymmetry_from_landmarks(fl.landmark, frame.shape)
                current_ai = float(ai)
                cv2.putText(frame, f"AI: {current_ai:.3f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Face not detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # HUD overlay
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            if recording:
                cv2.putText(frame, "REC ●", (540, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                ai_log.append((time.time(), current_ai))

            cv2.imshow("StrokeAI - NetLag HUD", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                if not recording:
                    ai_log = []
                    start_time = time.time()
                    recording = True
                    print("🎥 Recording started...")
                else:
                    recording = False
                    duration = time.time() - start_time if start_time is not None else 0
                    print(f"🛑 Recording stopped. {len(ai_log)} samples, {duration:.1f}s")
                    _save_csv(ai_log)

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
