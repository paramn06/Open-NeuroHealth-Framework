import os, sys, glob, subprocess, platform, json

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(ROOT, ".."))  # repo root
TOOLS = os.path.join(ROOT, "tools")
LOG_DIR = os.path.join(ROOT, "data", "logs")

def latest_csv():
    files = glob.glob(os.path.join(LOG_DIR, "face_ai_session_*.csv"))
    return max(files, key=os.path.getmtime) if files else None

def run_strokeai():
    mod = "modules.stroke.features.face_asymmetry"
    return subprocess.call([sys.executable, "-m", mod])

def plot_latest():
    csv_path = latest_csv()
    if not csv_path:
        print("❌ No CSV found in data/logs. Record a session first (menu option 1).")
        return 1
    py = os.path.join(TOOLS, "plot_ai.py")
    return subprocess.call([sys.executable, py, csv_path])

def cam_probe():
    py = os.path.join(TOOLS, "cam_probe.py")
    return subprocess.call([sys.executable, py])

def system_check():
    py = os.path.join(TOOLS, "system_check.py")
    if not os.path.isfile(py):
        print("⚠️ tools/system_check.py not found.")
        return 1
    return subprocess.call([sys.executable, py])

def main():
    while True:
        print("\n=== Open NeuroHealth — StrokeAI Demo ===")
        print("1) Run StrokeAI (webcam, record CSV/JSON)")
        print("2) Plot latest session CSV")
        print("3) Camera probe")
        print("4) System check")
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
        elif choice == "q":
            break
        else:
            print("Invalid choice.")
    print("Bye.")

if __name__ == "__main__":
    main()
