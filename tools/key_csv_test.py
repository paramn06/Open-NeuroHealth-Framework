# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------
import cv2, csv, os, time
from datetime import datetime
import numpy as np

# Make sure folders exist
os.makedirs("data/logs", exist_ok=True)

print("📹 KEY CSV TEST")
print("Press 'r' to start/stop, 'q' to quit")

recording = False
log = []
start_t = None

# Create blank image for testing
frame = np.ones((240, 320, 3), dtype=np.uint8) * 255

while True:
    cv2.putText(frame, f"REC={recording}  samples={len(log)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255) if not recording else (0, 255, 0), 2)

    cv2.imshow("KEY CSV TEST", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        if not recording:
            log.clear()
            start_t = time.time()
            recording = True
            print("🎥 Recording started…")
        else:
            recording = False
            duration = time.time() - start_t if start_t else 0
            print(f"🛑 Recording stopped. {len(log)} samples, {duration:.1f}s")

            if log:
                csv_path = f"data/logs/key_test_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["t_sec", "value"])
                    t0 = log[0][0]
                    for t, v in log:
                        writer.writerow([t - t0, v])
                print(f"✅ CSV saved → {csv_path}")
            else:
                print("⚠️ No samples collected")

    elif key == ord('q'):
        print("👋 Exiting.")
        break

    if recording:
        log.append((time.time(), len(log)))  # fake data stream

cv2.destroyAllWindows()
