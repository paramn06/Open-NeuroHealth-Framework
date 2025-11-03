# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------

import sounddevice as sd

CANDS_FS = [16000, 24000, 44100, 48000]
CANDS_CH = [1, 2]

def main():
    devs = sd.query_devices()
    print("🎙️ Input devices:")
    idx_map = []
    for i, d in enumerate(devs):
        if d["max_input_channels"] > 0:
            print(f"{i:2d}: {d['name']}  (in={d['max_input_channels']})  hostapi={sd.query_hostapis()[d['hostapi']]['name']}")
            idx_map.append(i)

    pick = input("\nEnter device index (or Enter for default): ").strip()
    device = int(pick) if pick else None

    print("\n🔎 Probing formats...")
    for fs in CANDS_FS:
        for ch in CANDS_CH:
            try:
                sd.check_input_settings(device=device, samplerate=fs, channels=ch)
                print(f"✅ OK: fs={fs} Hz, channels={ch}")
            except Exception as e:
                print(f"❌ fs={fs}, ch={ch} -> {e}")

    # If something passes, try 3s capture/playback with the first OK combo
    for fs in CANDS_FS:
        for ch in CANDS_CH:
            try:
                sd.check_input_settings(device=device, samplerate=fs, channels=ch)
                print(f"\n⏺️ Recording 3s @ {fs} Hz, ch={ch} ...")
                x = sd.rec(int(3*fs), samplerate=fs, channels=ch, dtype="float32", device=device)
                sd.wait()
                print("▶️ Playback...")
                sd.play(x, fs); sd.wait()
                print("✅ Worked.")
                return
            except Exception:
                continue

    print("\n⚠️ No working combo found. Try a different device index.")
if __name__ == "__main__":
    main()
