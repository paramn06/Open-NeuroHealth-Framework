import sys, time, numpy as np, sounddevice as sd

def rms_db(x):
    eps = 1e-12
    return 20*np.log10(np.sqrt((x**2).mean() + eps))

def main():
    if len(sys.argv) < 4:
        print("Usage: python tools/mic_meter.py <device_index> <fs> <channels>")
        sys.exit(1)
    device = int(sys.argv[1])
    fs = int(sys.argv[2])
    ch = int(sys.argv[3])

    sd.check_input_settings(device=device, samplerate=fs, channels=ch)

    print(f"🎙️ Live mic meter — device={device}, fs={fs}, ch={ch}")
    print("Press Ctrl+C to stop.")
    block = 0.2
    with sd.InputStream(device=device, samplerate=fs, channels=ch,
                        dtype='float32', blocksize=int(fs*block)) as stream:
        while True:
            frames, overflowed = stream.read(int(fs*block))
            x = frames[:,0] if frames.ndim>1 else frames
            level = rms_db(x)
            n = int(np.clip((level + 60), 0, 60))
            bar = "#"*n + "-"*(60-n)
            print(f"\r{level:6.1f} dBFS |{bar}|", end="", flush=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye 👋")
