import os, time, json, statistics, csv, sys
from datetime import datetime
import numpy as np
import cv2
import mediapipe as mp

# --- Minimal asymmetry from your module (avoids import issues) ---
L_EYE, R_EYE = 33, 263
PAIRS = [(61, 291), (133, 362), (33, 263)]
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

def _pt(landmarks, idx, w, h):
    lm = landmarks[idx]
    return np.array([lm.x * w, lm.y * h], dtype=np.float32)

def compute_ai(landmarks, image_shape):
    h, w = image_shape[:2]
    eps = 1e-6
    iod = np.linalg.norm(_pt(landmarks, R_EYE, w, h) - _pt(landmarks, L_EYE, w, h)) + eps
    lref = _pt(landmarks, L_EYE, w, h)
    rref = _pt(landmarks, R_EYE, w, h)
    diffs, LsRs = [], []
    for L_idx, R_idx in PAIRS:
        Lp = _pt(landmarks, L_idx, w, h); Rp = _pt(landmarks, R_idx, w, h)
        L_vert = abs(Lp[1] - lref[1]) / iod
        R_vert = abs(Rp[1] - rref[1]) / iod
        diffs.append(abs(L_vert - R_vert))
        LsRs.append(L_vert + R_vert)
    ai = float(np.mean(diffs) / (np.mean(LsRs) + eps))
    return ai

def run_session(seconds=10, device_index=0, backend="DSHOW"):
    cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW if backend=="DSHOW" else cv2.CAP_MSMF)
    if not cap.isOpened():
        return {"ok": False, "err": f"camera open failed (idx={device_index}, backend={backend})"}

    ai_vals, fps_vals, frames, start = [], [], 0, time.time()
    err_no_face = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as fm:
        while time.time() - start < seconds:
            ok, frame = cap.read()
            if not ok:
                break
            t0 = time.time()
            res = fm.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if res.multi_face_landmarks:
                ai = compute_ai(res.multi_face_landmarks[0].landmark, frame.shape)
                ai_vals.append(ai)
            else:
                err_no_face += 1
            frames += 1
            fps_vals.append(1.0 / max(time.time()-t0, 1e-6))
    cap.release()

    dur = time.time() - start
    if frames == 0:
        return {"ok": False, "err": "no frames read"}

    stats = {
        "ok": True,
        "frames": frames,
        "duration_sec": round(dur,2),
        "fps_avg": round(statistics.mean(fps_vals),2),
        "fps_min": round(min(fps_vals),2),
        "fps_p10": round(np.percentile(fps_vals,10),2),
        "fps_p90": round(np.percentile(fps_vals,90),2),
        "ai_count": len(ai_vals),
        "ai_mean": round(statistics.mean(ai_vals),5) if ai_vals else None,
        "ai_std": round(statistics.pstdev(ai_vals),5) if len(ai_vals)>1 else 0.0,
        "no_face_frames": err_no_face,
        "backend": backend,
        "device_index": device_index,
    }
    return stats

def main():
    os.makedirs("data/stability", exist_ok=True)
    tag = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    csv_path = f"data/stability/webcam_stability_{tag}.csv"
    json_path = f"data/stability/webcam_stability_{tag}.json"

    # Run multiple sessions back-to-back
    SESSIONS = [
        {"seconds": 8, "device_index": 0, "backend": "DSHOW"},
        {"seconds": 8, "device_index": 0, "backend": "MSMF"},
        {"seconds": 15, "device_index": 0, "backend": "DSHOW"},
    ]

    rows, summary = [], {"runs":[]}
    for i, cfg in enumerate(SESSIONS, 1):
        print(f"▶️  Session {i}: {cfg}")
        res = run_session(**cfg)
        res["session"] = i
        res["ts"] = datetime.utcnow().isoformat()+"Z"
        rows.append(res)
        summary["runs"].append(res)

    # Write CSV (flat)
    keys = sorted(set().union(*[r.keys() for r in rows]))
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Write JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Stability CSV → {csv_path}")
    print(f"✅ Stability JSON → {json_path}")

if __name__ == "__main__":
    main()
