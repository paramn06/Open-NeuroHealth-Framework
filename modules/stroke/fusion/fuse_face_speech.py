# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

# modules/stroke/fusion/fuse_face_speech.py
# Read latest Neuro Unit files for face & speech; output fused risk JSON.

# modules/stroke/fusion/fuse_face_speech.py
"""
Fuse Face Asymmetry (AI) + Speech Rate into a simple stroke-risk prototype.
- Loads latest Face AI avg JSON and Speech rate JSON
- Computes risks and overall risk (0..1)
- Shows a small bar chart (Face, Speech, Overall)
- Saves data/exports/stroke_risk_fused.json
"""

import os, json, glob, math
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

FACE_GLOB = "data/exports/neuro_unit_face_ai_avg.json"       # we overwrite this file each save
SPEECH_GLOB = "data/exports/neuro_unit_speech_rate.json"     # we overwrite this file each save
OUT_JSON = "data/exports/stroke_risk_fused.json"

def _load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return None

def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))

def _face_risk(face_ai):
    """
    Map asymmetry index (lower is better) to risk 0..1.
    Rough heuristic:
      <= 0.02 -> ~0 risk (very symmetric)
      0.02..0.12 -> rising risk
      >= 0.12 -> ~1 risk
    """
    return _clamp((face_ai - 0.02) / (0.12 - 0.02))

def _speech_risk(sps, voiced_ratio):
    """
    Map speech rate (syll/sec) + voiced ratio to risk 0..1.
    Heuristic:
      Normal conversational ~3–7 syll/sec.
      If sps < 3, risk grows; also penalize very low voiced_ratio.
    """
    # risk from slow speech
    r_sps = _clamp((3.0 - float(sps)) / 2.0)  # 3 -> 0, 1 -> 1 (cap 0..1)
    # risk from low voicing
    r_vr = _clamp((0.5 - float(voiced_ratio)) / 0.25)  # <=0.25 -> 1, >=0.5 -> 0
    # combine (soft OR)
    return _clamp(0.7 * r_sps + 0.3 * r_vr)

def _grade(r):
    if r < 0.3:
        return "LOW", "Proceed normally"
    if r < 0.6:
        return "MODERATE", "Observe carefully / retest"
    return "HIGH", "Seek medical attention if symptoms persist"

def fuse_and_plot():
    # --- load inputs ---
    face = _load_json(FACE_GLOB)
    speech = _load_json(SPEECH_GLOB)

    if face is None:
        print("⚠️ Face JSON not found. Run menu [1] first to save averaged AI JSON.")
    if speech is None:
        print("⚠️ Speech JSON not found. Run menu [5] to record speech JSON.")
    if face is None or speech is None:
        return

    # --- read values ---
    face_ai = float(face["signals"].get("face_asymmetry_avg", np.nan))
    sps = float(speech["signals"].get("speech_syllables_per_sec", np.nan))
    voiced_ratio = float(speech["signals"].get("voiced_ratio", np.nan))

    if np.isnan(face_ai) or np.isnan(sps) or np.isnan(voiced_ratio):
        print("⚠️ Missing numeric values in inputs.")
        return

    # --- compute risks ---
    r_face = _face_risk(face_ai)
    r_speech = _speech_risk(sps, voiced_ratio)
    # overall (weight face a bit higher in this prototype)
    overall = _clamp(0.6 * r_face + 0.4 * r_speech)

    label, suggestion = _grade(overall)

    # --- print summary ---
    print("\n=== StrokeAI Fusion Summary ===")
    print(f" Face AI avg:     {face_ai:.3f}  -> face risk {r_face:.2f}")
    print(f" Speech rate sps: {sps:.2f}  (voiced {voiced_ratio:.2f}) -> speech risk {r_speech:.2f}")
    print(f" Overall risk:    {overall:.2f}  [{label}]  — {suggestion}")

    # --- save JSON ---
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    out = {
        "id": face.get("id", "") or speech.get("id", ""),
        "module": "stroke",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "inputs": {
            "face_json": FACE_GLOB,
            "speech_json": SPEECH_GLOB
        },
        "signals": {
            "risk_face": r_face,
            "risk_speech": r_speech,
            "risk_overall": overall,
            "face_ai_avg": face_ai,
            "speech_sps": sps,
            "voiced_ratio": voiced_ratio
        },
        "notes": "Prototype fusion; not a medical device"
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"✅ Saved fused risk JSON → {OUT_JSON}")

    # --- plot small bar chart ---
    labels = ["Face", "Speech", "Overall"]
    vals = [r_face, r_speech, overall]

    plt.figure(figsize=(5, 3.2))
    plt.bar(labels, vals)          # (no custom colors/styles)
    plt.ylim(0, 1)
    plt.ylabel("Risk (0–1)")
    plt.title(f"StrokeAI Fusion — Overall: {overall:.2f} [{label}]")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    fuse_and_plot()
