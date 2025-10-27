# tools/env_check.py
import sys, platform, os, importlib
print("🧪 Open NeuroHealth – Environment Check\n")

# Basics
print(f"Python: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"CWD: {os.getcwd()}\n")

def ok(mod, attr=None):
    try:
        m = importlib.import_module(mod)
        v = getattr(m, attr) if attr else getattr(m, "__version__", "OK")
        print(f"✅ {mod} {v}")
        return True
    except Exception as e:
        print(f"❌ {mod} – {e}")
        return False

have_cv2 = ok("cv2", "__version__")
have_mp = ok("mediapipe", "__version__")
have_np = ok("numpy", "__version__")
have_matplot = ok("matplotlib", "__version__")
have_sd = ok("sounddevice", "__version__")
have_pytest = ok("pytest")

# Probe webcam (non-intrusive single frame)
if have_cv2:
    import cv2
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    print(f"\n🎥 Webcam opened: {cap.isOpened()}")
    if cap.isOpened():
        ok_read, _ = cap.read()
        print(f"Frame read: {ok_read}")
        cap.release()

# List microphones
if have_sd:
    import sounddevice as sd
    print("\n🎙️ Audio input devices:")
    for i, d in enumerate(sd.query_devices()):
        if d.get("max_input_channels", 0) > 0:
            print(f"  {i}: {d['name']} (in={d['max_input_channels']})")

# Repo structure sanity
expected = ["modules", "onf", "data", "tools"]
missing = [p for p in expected if not os.path.isdir(p)]
print("\n📂 Structure:", "OK" if not missing else f"Missing {missing}")

print("\n✅ Env check complete.")
