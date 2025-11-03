# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

# app/strokeai_demo.py
# Open NeuroHealth — StrokeAI Demo Launcher

import sys, os, subprocess, glob

PY = sys.executable

def run_strokeai():
    print("\n🎥 Launching StrokeAI (webcam)…\n")
    subprocess.run([PY, "modules/stroke/features/face_asymmetry.py"])

def plot_latest():
    print("\n📈 Plotting latest CSV…\n")
    paths = glob.glob("data/logs/face_ai_session_*.csv")
    if not paths:
        print("⚠️ No CSV found in data/logs. Record once with option 1.")
        return
    latest = max(paths, key=os.path.getmtime)
    subprocess.run([PY, "tools/plot_ai.py", latest])

def cam_probe():
    print("\n🔎 Camera probe…\n")
    subprocess.run([PY, "tools/cam_probe.py"])

def system_check():
    print("\n🧪 System check…\n")
    subprocess.run([PY, "tools/system_check.py"])

def run_speech():
    print("\n🎙️ Speech rate recorder…\n")
    subprocess.run([PY, "modules/stroke/features/speech_rate.py"])

def fuse_face_speech():
    print("\n🧠 Fusing Face + Speech signals…\n")
    subprocess.run([PY, "modules/stroke/fusion/fuse_face_speech.py"])

def main():
    while True:
        print("\n=== Open NeuroHealth — StrokeAI Demo ===")
        print("1) Run StrokeAI (webcam, record CSV/JSON)")
        print("2) Plot latest session CSV")
        print("3) Camera probe")
        print("4) System check")
        print("5) Record speech (syll/sec JSON)")
        print("6) Fuse Face + Speech (risk JSON)")
        print("q) Quit")
        choice = input("Select: ").strip().lower()

        if choice == "1":
            run_strokeai()
        elif choice == "2":
            plot_latest()
        elif choice == "3":
            cam_probe()
        elif choice == "4":
            system_check()
        elif choice == "5":
            run_speech()
        elif choice == "6":
            fuse_face_speech()
        elif choice == "q":
            break
        else:
            print("❓ Not a valid option.")

if __name__ == "__main__":
    main()
