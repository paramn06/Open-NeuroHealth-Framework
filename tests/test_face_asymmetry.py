import numpy as np
from modules.stroke.features.face_asymmetry import compute_asymmetry_from_landmarks

class Dummy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_ai_symmetric_face():
    # Make synthetic perfectly symmetric landmarks around y=0.5
    w, h = 640, 480
    coords = {
        33: (0.3, 0.5), 263: (0.7, 0.5),
        61: (0.3, 0.6), 291: (0.7, 0.6),
        133: (0.4, 0.5), 362: (0.6, 0.5)
    }
    max_idx = max(coords.keys())
    lms = [Dummy(0, 0) for _ in range(max_idx + 1)]
    for k, (x, y) in coords.items():
        lms[k] = Dummy(x, y)

    ai, _ = compute_asymmetry_from_landmarks(lms, (h, w, 3))
    assert ai < 1e-3
