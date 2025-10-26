import os, glob, sys, subprocess

LOGS = sorted(glob.glob("data/logs/face_ai_session_*.csv"))
if not LOGS:
    print("No logs found. Run StrokeAI and press r…r to record.")
    sys.exit(0)

for i,f in enumerate(LOGS,1):
    print(f"{i:2d}) {f}")

choice = input("Select a log to plot (number, or Enter for latest): ").strip()
if choice.isdigit() and 1 <= int(choice) <= len(LOGS):
    path = LOGS[int(choice)-1]
else:
    path = LOGS[-1]
print("Plotting:", path)
subprocess.call([sys.executable, "tools/plot_ai.py", path])
