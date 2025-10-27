# modules/stroke/features/speech_rate.py
from datetime import datetime
import uuid, os, json, argparse
import numpy as np
import sounddevice as sd
from scipy.signal import medfilt

def record(duration, fs, channels, device=None):
    print(f"🎙️ Recording {duration}s @ {fs} Hz, ch={channels} ... Speak naturally.")
    x = sd.rec(int(duration*fs), samplerate=fs, channels=channels, dtype="float32", device=device)
    sd.wait()
    return x[:,0] if channels > 1 else x[:,0]

def frame_signal(x, fs, win_ms=30, hop_ms=10):
    win = int(fs*win_ms/1000)
    hop = int(fs*hop_ms/1000)
    n = max(0, (len(x)-win)//hop + 1)
    frames = np.stack([x[i*hop:i*hop+win] for i in range(n)], axis=0) if n>0 else np.empty((0,win))
    return frames, win, hop

def estimate_syllables_per_sec(x, fs):
    if x.size == 0:
        return 0.0, 0.0
    frames, win, hop = frame_signal(x, fs)
    if frames.size == 0:
        return 0.0, 0.0
    energy = (frames**2).mean(axis=1)
    zcr = (np.abs(np.diff(np.sign(frames), axis=1))>0).mean(axis=1)
    energy_s = medfilt(energy, kernel_size=7)
    zcr_s = medfilt(zcr, kernel_size=7)
    e_th = np.percentile(energy_s, 65)
    z_th = np.percentile(zcr_s, 35)
    voiced = (energy_s > e_th) & (zcr_s < z_th)
    islands = np.logical_and(voiced, np.concatenate([[False], ~voiced[:-1]])).sum()
    dur_sec = len(x)/fs
    voiced_ratio = float(voiced.mean()) if voiced.size else 0.0
    sps = float(islands / max(dur_sec, 1e-6))
    return sps, voiced_ratio

def save_neuro_unit_speech(sps, voiced_ratio, duration, fs, device_label, path="data/exports/neuro_unit_speech_rate.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = {
        "id": str(uuid.uuid4()),
        "module": "stroke",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "signals": {
            "speech_syllables_per_sec": float(sps),
            "voiced_ratio": float(voiced_ratio),
            "duration_sec": duration,
            "fs_hz": fs
        },
        "device": device_label,
        "notes": "speech rate prototype"
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"✅ Saved Speech Neuro Unit → {path}")
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", type=int, default=None, help="Input device index (see tools/audio_probe.py)")
    ap.add_argument("--fs", type=int, default=16000, help="Sample rate")
    ap.add_argument("--channels", type=int, default=1, help="Channels (1 or 2)")
    ap.add_argument("--duration", type=float, default=5.0, help="Seconds to record")
    args = ap.parse_args()

    # Validate settings before recording
    try:
        sd.check_input_settings(device=args.device, samplerate=args.fs, channels=args.channels)
    except Exception as e:
        print("❌ Settings invalid:", e)
        print("Tip: run  python tools\\audio_probe.py  to find working (fs, channels) for your device.")
        return

    x = record(duration=args.duration, fs=args.fs, channels=args.channels, device=args.device)
    sps, vr = estimate_syllables_per_sec(x, args.fs)
    print(f"📏 Estimated speech rate: {sps:.2f} syll/sec (voiced ratio: {vr:.2f})")
    label = f"device={args.device}" if args.device is not None else "default-mic"
    save_neuro_unit_speech(sps, vr, args.duration, args.fs, label)

if __name__ == "__main__":
    main()
