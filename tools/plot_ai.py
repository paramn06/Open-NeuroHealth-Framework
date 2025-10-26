import csv, sys, os, glob
import numpy as np
import matplotlib.pyplot as plt

LOG_DIR = "data/logs"

def find_latest_csv():
    files = glob.glob(os.path.join(LOG_DIR, "face_ai_session_*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def main():
    # If a path is provided, use it; otherwise, pick the latest CSV
    if len(sys.argv) >= 2:
        csv_path = sys.argv[1]
        if not os.path.isfile(csv_path):
            print(f"❌ File not found: {csv_path}")
            sys.exit(1)
    else:
        csv_path = find_latest_csv()
        if not csv_path:
            print("❌ No CSV found in data/logs/. Record a session (r…r) first.")
            sys.exit(1)
        print(f"ℹ️ No file provided. Using latest: {csv_path}")

    # Read CSV
    t, ai = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            t.append(float(row["t_sec"]))
            ai.append(float(row["ai"]))

    if not t:
        print("❌ CSV has no rows. Make sure you pressed 'r' to start and stop recording.")
        sys.exit(1)

    t = np.array(t)
    ai = np.array(ai)

    # Smoothing
    window = 10
    if len(ai) > window:
        ai_smooth = np.convolve(ai, np.ones(window)/window, mode="valid")
        t_smooth = t[:len(ai_smooth)]
    else:
        ai_smooth = ai
        t_smooth = t

    # Plot
    plt.figure(figsize=(8, 4.5))
    plt.plot(t, ai, label="Raw AI", color="gray", alpha=0.4, linewidth=1)
    plt.plot(t_smooth, ai_smooth, label=f"Smoothed (n={window})", color="blue", linewidth=2)

    # Zones
    plt.axhspan(0.00, 0.03, color="green",  alpha=0.15, label="Normal symmetry")
    plt.axhspan(0.03, 0.06, color="yellow", alpha=0.15, label="Slight asymmetry")
    plt.axhspan(0.06, max(0.1, ai.max()*1.1), color="red", alpha=0.12, label="High asymmetry")

    plt.xlabel("Time (s)")
    plt.ylabel("Asymmetry Index (AI)")
    plt.title(f"Facial Asymmetry Trace\n{os.path.basename(csv_path)}")
    plt.legend(loc="upper right", fontsize=8)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    # Save PNG
    out_dir = "data/plots"
    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, os.path.basename(csv_path).replace(".csv", ".png"))
    plt.savefig(png_path, dpi=160)
    print(f"🖼️ Saved plot → {png_path}")

    plt.show()

if __name__ == "__main__":
    main()
