# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

import cv2

# Try DSHOW first; switch to CAP_MSMF if needed
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("opened(DSHOW):", cap.isOpened())
if not cap.isOpened():
    cap.release()
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    print("opened(MSMF):", cap.isOpened())

cv2.namedWindow("Cam View (press q)", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Cam View (press q)", 960, 540)

while True:
    ok, frame = cap.read()
    if not ok or frame is None:
        print("read fail"); break
    cv2.imshow("Cam View (press q)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
