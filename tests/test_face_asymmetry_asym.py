import numpy as np
from modules.stroke.features.face_asymmetry import compute_asymmetry_from_landmarks

class Dummy:
    def __init__(self, x, y):
        self.x = x; self.y = y

def _make_landmarks(coords):
    max_idx = max(coords.keys())
    lms = [Dummy(0,0) for _ in range(max_idx+1)]
    for k,(x,y) in coords.items():
        lms[k] = Dummy(x,y)
    return lms

def test_ai_higher_for_asymmetric_vs_symmetric():
    w,h = 640,480
    # Symmetric reference
    sym = {
        33:(0.3,0.5), 263:(0.7,0.5),   # outer eye corners
        61:(0.3,0.6), 291:(0.7,0.6),   # mouth corners
        133:(0.4,0.5), 362:(0.6,0.5),  # inner eye corners
    }
    # Asymmetric: move right mouth corner down
    asym = dict(sym)
    asym[291] = (0.7, 0.65)

    ai_sym, _  = compute_asymmetry_from_landmarks(_make_landmarks(sym),  (h,w,3))
    ai_asym, _ = compute_asymmetry_from_landmarks(_make_landmarks(asym), (h,w,3))

    assert ai_asym > ai_sym
