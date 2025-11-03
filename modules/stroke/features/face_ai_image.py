# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

import sys, cv2, mediapipe as mp, numpy as np
from face_asymmetry import compute_asymmetry_from_landmarks

mp_face_mesh = mp.solutions.face_mesh


def run(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"Could not read {path}")
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as fm:
        res = fm.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not res.multi_face_landmarks:
            raise SystemExit("No face detected")
        lm = res.multi_face_landmarks[0].landmark
        ai, details = compute_asymmetry_from_landmarks(lm, img.shape)
        print(f"AI (static): {ai:.3f}  details: {details}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python face_ai_image.py <image_path>")
    else:
        run(sys.argv[1])
