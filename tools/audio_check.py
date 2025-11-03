# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------
import sounddevice as sd
import numpy as np

def list_inputs():
    print("🎙️ Input devices:")
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            print(f"{i:2d}: {dev['name']}  (in={dev['max_input_channels']})")

def record_play(seconds=3, fs=16000, device=None):
    print(f"\n⏺️ Recording {seconds}s @ {fs} Hz ...")
    x = sd.rec(int(seconds*fs), samplerate=fs, channels=1, dtype="float32", device=device)
    sd.wait()
    print("▶️  Playing back...")
    sd.play(x, fs); sd.wait()
    print("✅ Done")
    return x

if __name__ == "__main__":
    list_inputs()
    ans = input("\nEnter device index to test (or Enter for default): ").strip()
    dev = int(ans) if ans else None
    record_play(device=dev)
