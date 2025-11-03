# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------
import cv2, csv, os, time
from datetime import datetime

# Ensure output dir
os.makedirs("data/logs", exist_ok=True)

print("🎛️ NetLag HUD Test")
print("Keys: r=start/stop CSV logging, q=quit")

# try DSHOW first (most reliable on Windows), fallback to default
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Could not open webcam.")
    raise SystemExit

rec = False
log = []
t0 = None
fps = 0.0
last_t = time.time()

while True:
    ok, frame = cap.read()
    if not ok:
        print("⚠️ cap.read() failed")
        break

    # FPS estimate (EWMA)
    now = time.time()
    dt = now - last_t
    if dt > 0:
        fps = 0.9 * fps + 0.1 * (1.0 / dt)
    last_t = now

    # HUD: FPS + REC
    hud_color = (0, 255, 255)
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, hud_color, 2)
    if rec:
        cv2.putText(frame, "REC ●", (540, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    # If recording, append a simple signal (frame index over time)
    if rec:
        log.append((time.time(), len(log)))

    cv2.imshow("NetLag HUD (FPS + REC)", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        if not rec:
            log.clear()
            t0 = time.time()
            rec = True
            print("🎥 Recording started…")
        else:
            rec = False
            dur = time.time() - t0 if t0 else 0
            print(f"🛑 Recording stopped. samples={len(log)}, dur={dur:.1f}s")
            if log:
                csv_path = f"data/logs/netlag_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["t_sec", "value"])
                    base = log[0][0]
                    for t, v in log:
                        w.writerow([t - base, v])
                print("✅ CSV saved →", csv_path)
            else:
                print("⚠️ No samples collected; CSV not written.")

    elif key == ord('q'):
        print("👋 Quit.")
        break

cap.release()
cv2.destroyAllWindows()
