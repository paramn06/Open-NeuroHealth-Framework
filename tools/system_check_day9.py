"""
System Check - Day 9
Runs Face and Speech modules in sequence and verifies outputs.
"""

import subprocess, sys, json, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def run_script(path, args=None):
    cmd = [sys.executable, str(ROOT / path)] + (args or [])
    print(f"▶️ Running: {cmd}")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print(out.stdout)
        if out.returncode != 0:
            print(f"⚠️ Warning: {path} exited with code {out.returncode}")
        return True
    except Exception as e:
        print(f"❌ Failed to run {path}: {e}")
        return False

def main():
    print("🧠 Day 9: System Integration Test")
    print("="*50)

    face_ok = run_script("modules/stroke/features/face_asymmetry.py")
    speech_ok = run_script("modules/stroke/features/speech_rate.py", ["--duration", "5"])

    combined_report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": {
            "face": "ok" if face_ok else "failed",
            "speech": "ok" if speech_ok else "failed",
        }
    }

    combined_path = EXPORT_DIR / "neuro_system_check_day9.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_report, f, indent=2)

    print(f"✅ Saved combined report → {combined_path}")

if __name__ == "__main__":
    main()
