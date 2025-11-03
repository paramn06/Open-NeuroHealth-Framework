import numpy as np
import pytest
from modules.stroke.features.face_asymmetry import compute_asymmetry_from_landmarks

class Dummy:
    def __init__(self, x=0.0, y=0.0):
        self.x = x; self.y = y

def test_ai_handles_missing_landmarks_gracefully():
    # Provide a too-short landmarks list; function should not crash
    lms = [Dummy(0.0, 0.0)] * 10  # far fewer than needed indices
    ai, details = compute_asymmetry_from_landmarks(lms, (480, 640, 3))
    assert isinstance(ai, float)
