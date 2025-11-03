# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

# modules/stroke/features/speech_rate.py
"""
Speech rate (syllables/sec) + voiced ratio prototype
- Lists mic devices (--list)
- Records audio with chosen device
- Adjustable sensitivity (energy/ZCR percentiles)
- Saves WAV + Neuro Unit JSON
"""

from datetime import datetime
import uuid, os, json, argparse
import numpy as np
import sounddevice as sd
from scipy.signal import medfilt
from scipy.io import wavfile

# ----------------------------
# Helpers
# ----------------------------

def list_devices():
    print("🎙️ Input devices:")
    devs = sd.query_devices()
    for i, d in enumerate(devs):
        if d.get("max_input_channels", 0) > 0:
            print(f" {i:2d}: {d['name']}  (in={d['max_input_channels']})")
    print("\nTip: pick an index with nonzero 'in='.\n")

def ensure_dirs():
    os.makedirs("data/exports", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

def record(duration, fs, channels, device=None):
    print(f"🎙️ Recording {duration:.1f}s @ {fs} Hz, ch={channels} (device={device}) … Speak naturally.")
    x = sd.rec(int(duration*fs), samplerate=fs, channels=channels, dtype="float32", device=device)
    sd.wait()
    x = x.squeeze()  # (N,) if mono, (N,C) -> (N,)
    return x

def frame_signal(x, fs, win_ms=30, hop_ms=10):
    win = int(fs*win_ms/1000)
    hop = int(fs*hop_ms/1000)
    if win < 3: win = 3
    if hop < 1: hop = 1
    n = max(0, (len(x)-win)//hop + 1)
    if n <= 0:
        return np.empty((0, win), dtype=x.dtype), win, hop
    frames = np.stack([x[i*hop:i*hop+win] for i in range(n)], axis=0)
    return frames, win, hop

def estimate_syllables_per_sec(x, fs, energy_pctl=40, zcr_pctl=60, agc=False, debug=False):
    """
    energy_pctl: lower = more sensitive to quiet speech (default 40)
    zcr_pctl:    higher = more tolerant to consonants/noise (default 60)
    agc:         normalize to unit RMS before analysis
    """
    x = np.asarray(x, dtype=np.float32)
    if x.size == 0:
        return 0.0, 0.0, {"frames": 0, "voiced_frames": 0, "mean_abs_amp": 0.0}

    mean_abs_amp = float(np.mean(np.abs(x)))
    if agc and mean_abs_amp > 0:
        x = x / max(np.sqrt(np.mean(x**2)), 1e-6)

    frames, win, hop = frame_signal(x, fs)
    if frames.size == 0:
        return 0.0, 0.0, {"frames": 0, "voiced_frames": 0, "mean_abs_amp": mean_abs_amp}

    # Features
    energy = (frames**2).mean(axis=1)
    # zero-cross rate per frame
    signs = np.sign(frames)
    zcr = (np.abs(np.diff(signs, axis=1)) > 0).mean(axis=1)

    # Smooth with median filter (kernel must be odd)
    k = 7 if len(energy) >= 7 else max(3, (len(energy)//2)*2+1)
    energy_s = medfilt(energy, kernel_size=k)
    zcr_s = medfilt(zcr, kernel_size=k)

    # Thresholds
    e_th = np.percentile(energy_s, np.clip(energy_pctl, 1, 99))
    z_th = np.percentile(zcr_s, np.clip(zcr_pctl, 1, 99))

    # Voiced heuristic
    voiced = (energy_s > e_th) & (zcr_s < z_th)

    # Count 'islands' (rising edges of voiced)
    if voiced.size:
        islands = int(np.logical_and(voiced, np.concatenate([[False], ~voiced[:-1]])).sum())
    else:
        islands = 0

    dur_sec = len(x)/fs
    voiced_ratio = float(voiced.mean()) if voiced.size else 0.0
    sps = float(islands / max(dur_sec, 1e-6))

    details = {
        "frames": int(len(energy)),
        "voiced_frames": int(voiced.sum()),
        "mean_abs_amp": mean_abs_amp,
        "energy_pctl": energy_pctl,
        "zcr_pctl": zcr_pctl,
        "islands": islands,
        "duration_sec": dur_sec
    }

    if debug:
        print(f"Debug: frames={len(energy)}, voiced={voiced.sum()} ({voiced_ratio:.2f})")
        print(f"Debug: islands={islands}, duration={dur_sec:.2f}, sps={sps:.2f}")
        print(f"Debug: mean|x|={mean_abs_amp:.4f}, e_th={e_th:.6g}, z_th={z_th:.6g}")

    return sps, voiced_ratio, details

def save_wav(x, fs, path="data/exports/last_speech.wav"):
    ensure_dirs()
    # clip to int16 for wav
    y = np.clip(x, -1.0, 1.0)
    wavfile.write(path, fs, (y * 32767).astype(np.int16))
    print(f"💾 Saved WAV → {path}")
    return path

def save_neuro_unit_speech(sps, voiced_ratio, duration, fs, device_label, path="data/exports/neuro_unit_speech_rate.json"):
    ensure_dirs()
    record = {
        "id": str(uuid.uuid4()),
        "module": "stroke",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "signals": {
            "speech_syllables_per_sec": float(sps),
            "voiced_ratio": float(voiced_ratio),
            "duration_sec": float(duration),
            "fs_hz": int(fs)
        },
        "device": device_label,
        "notes": "speech rate prototype"
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"✅ Saved Speech Neuro Unit → {path}")
    return path

# ----------------------------
# CLI
# ----------------------------

def main():
    ap = argparse.ArgumentParser(description="Speech rate (syll/sec) + voiced ratio")
    ap.add_argument("--list", action="store_true", help="List input devices and exit")
    ap.add_argument("--device", type=int, default=None, help="Input device index")
    ap.add_argument("--fs", type=int, default=48000, help="Sample rate (Hz)")
    ap.add_argument("--channels", type=int, default=1, help="Channels (1=mono)")
    ap.add_argument("--duration", type=float, default=5.0, help="Seconds to record")
    ap.add_argument("--energy-pctl", type=float, default=40.0, help="Energy percentile threshold (lower = more sensitive)")
    ap.add_argument("--zcr-pctl", type=float, default=60.0, help="ZCR percentile threshold (higher = more tolerant)")
    ap.add_argument("--agc", action="store_true", help="Normalize input (auto-gain) before analysis")
    ap.add_argument("--debug", action="store_true", help="Print debug stats")
    args = ap.parse_args()

    if args.list:
        list_devices()
        return

    # Validate settings before recording
    try:
        sd.check_input_settings(device=args.device, samplerate=args.fs, channels=args.channels)
    except Exception as e:
        print("❌ Settings invalid:", e)
        print("Tip: run  python tools\\audio_probe.py  to find a working (device/fs/ch).")
        print("     or run with  --list  to see available input devices.")
        return

    # Record
    x = record(duration=args.duration, fs=args.fs, channels=args.channels, device=args.device)
    print(f"🔎 Mean |x| amplitude: {np.abs(x).mean():.5f}")
    save_wav(x, args.fs, "data/exports/last_speech.wav")

    # Analyze
    sps, vr, det = estimate_syllables_per_sec(
        x, args.fs,
        energy_pctl=args.energy_pctl,
        zcr_pctl=args.zcr_pctl,
        agc=args.agc,
        debug=args.debug
    )
    print(f"📏 Estimated speech rate: {sps:.2f} syll/sec  (voiced ratio: {vr:.2f})")

    # Persist Neuro Unit
    label = f"device={args.device}" if args.device is not None else "default-mic"
    save_neuro_unit_speech(sps, vr, args.duration, args.fs, label)

if __name__ == "__main__":
    main()
