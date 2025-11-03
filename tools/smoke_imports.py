# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------
import importlib, sys
for mod in [
    "cv2",
    "mediapipe",
    "numpy",
    "modules.stroke.features.face_asymmetry",
    "modules.stroke.features.speech_rate",
    "modules.stroke.fusion.fuse_face_speech",
]:
    try:
        importlib.import_module(mod)
        print(f"✅ import {mod}")
    except Exception as e:
        print(f"❌ import {mod}: {e}")
        sys.exit(1)
print("✅ All critical imports OK")
