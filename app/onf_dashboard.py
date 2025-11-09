# app/onf_dashboard.py
import os, json, glob, subprocess, sys
from pathlib import Path
import pandas as pd
import streamlit as st
# ---------- Force UTF-8 for Windows ----------
# Prevents 'charmap' codec decode errors when reading subprocess output
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

# ---------- Paths (auto-detected; no hard-coded C:\...) ----------
APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent                       # project root (parent of /app)
LOG_DIR = REPO / "data" / "logs"
EXPORT_DIR = REPO / "data" / "exports"
PY = sys.executable                         # the exact Python running Streamlit

LOG_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Open NeuroHealth — StrokeAI", layout="wide")
st.title("🧠 Open NeuroHealth — StrokeAI Dashboard")
st.caption("Minimal dashboard to view outputs and launch quick tasks")

with st.sidebar:
    st.header("Modules")
    tab = st.radio(
        "Go to",
        ["Face (CSV/JSON viewer)", "Speech (JSON viewer)", "Quick tasks"],
        index=0
    )
    st.markdown("---")
    st.caption(f"Repo: `{REPO}`")
    st.caption("Tip: generate data via the CLI first (camera/mic).")

# ---------- Helpers ----------
def latest(pattern: str) -> str | None:
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None

def run_py(args_list):
    """
    Run a Python script reliably even when the project path contains spaces
    (e.g., 'C:\\Users\\MY BOOK\\...'). Automatically resolves the script to an
    absolute path and avoids using 'cwd' to prevent FileNotFound errors.
    """

    import subprocess, sys, os
    from pathlib import Path
    import streamlit as st

    # --- Resolve script path ---
    script = Path(args_list[0])
    if not script.is_absolute():
        script = (REPO / script).resolve()

    # --- Build command ---
    cmd = [sys.executable, str(script)] + [str(a) for a in args_list[1:]]

    # --- Debug info ---
    st.write("```")
    st.write(f"📁 Repo: {REPO}")
    st.write(f"▶️  Command: {cmd}")
    st.write("```")

    try:
        # Environment (force UTF-8 for Windows)
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        env.setdefault("PYTHONUTF8", "1")

        # --- Run process safely ---
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        # --- Stream real-time output ---
        assert proc.stdout is not None
        for line in proc.stdout:
            st.write(line.rstrip())
        proc.wait()

        # --- Final result ---
        if proc.returncode == 0:
            st.success("✅ Process finished successfully")
        else:
            st.warning(f"⚠️ Process exited with code {proc.returncode}")
        return proc.returncode

    except FileNotFoundError as e:
        st.error(f"❌ File not found: {e}")
        st.info("Check that your file paths exist and that your REPO variable is correct.")
        return 1

    except Exception as e:
        st.error(f"💥 Unexpected error: {e}")
        return 1



# ---------- Face viewer ----------
if tab == "Face (CSV/JSON viewer)":
    st.subheader("Face Asymmetry Sessions (CSV)")
    col1, col2 = st.columns(2)

    with col1:
        csv_files = sorted(LOG_DIR.glob("face_ai_session_*.csv"))
        sel_csv_name = st.selectbox(
            "Choose a CSV session",
            [f.name for f in csv_files],
            index=(len(csv_files) - 1) if csv_files else None
        )
        uploaded_csv = st.file_uploader("...or upload a CSV", type=["csv"], key="face_csv_up")

        df = None
        chosen_csv_path = None  # Path to the CSV we’re visualizing

        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
            # When uploaded, we only know the *name*, not a repo path
            if getattr(uploaded_csv, "name", None):
                chosen_csv_path = Path(uploaded_csv.name)  # for PNG naming only
        elif sel_csv_name:
            chosen_csv_path = (LOG_DIR / sel_csv_name).resolve()
            df = pd.read_csv(chosen_csv_path)

        if df is not None and not df.empty:
            st.dataframe(df.head(50), width="stretch")
            if "t_sec" in df.columns and "ai" in df.columns:
                st.line_chart(df.set_index("t_sec")["ai"], width="stretch")
            else:
                st.info("CSV is missing expected columns ('t_sec', 'ai').")
        else:
            st.info("No CSV selected or file is empty.")


    with col2:
        st.subheader("Averaged JSON (latest)")
        json_path = EXPORT_DIR / "neuro_unit_face_ai_avg.json"
        if json_path.exists():
            j = json.load(open(json_path, "r", encoding="utf-8"))
            st.json(j)
        else:
            st.info("No averaged JSON found yet. Press **r** then **s** in the webcam app to generate one.")

        st.markdown("---")
        st.subheader("Saved Plot (PNG)")

        plots_dir = (REPO / "data" / "plots")
        plots_dir.mkdir(parents=True, exist_ok=True)

        # Guess the PNG name from the selected/uploaded CSV
        png_guess = None
        if chosen_csv_path is not None:
            png_guess = (plots_dir / (chosen_csv_path.stem + ".png")).resolve()

        # Buttons for convenience
        c1, c2 = st.columns(2)
        with c1:
            regen = st.button("Generate plot for this CSV")
        with c2:
            show_latest = st.button("Show latest plot in folder")

        # Generate (or re-generate) the PNG via tools/plot_ai.py if we have a repo CSV
        if regen:
            if chosen_csv_path and chosen_csv_path.exists():
                rc = run_py(["tools/plot_ai.py", str(chosen_csv_path)])



# ---------- Speech viewer ----------
elif tab == "Speech (JSON viewer)":
    st.subheader("Speech Neuro Unit (JSON)")
    json_files = sorted(EXPORT_DIR.glob("neuro_unit_speech_rate*.json"))
    sel_json_name = st.selectbox(
        "Choose a speech JSON",
        [f.name for f in json_files],
        index=(len(json_files)-1) if json_files else None
    )
    uploaded_json = st.file_uploader("...or upload a JSON", type=["json"], key="speech_json_up")

    js = None
    if uploaded_json is not None:
        js = json.load(uploaded_json)
    elif sel_json_name:
        js = json.load(open(EXPORT_DIR / sel_json_name, "r", encoding="utf-8"))

    if js:
        st.json(js)
        s = js.get("signals", {})
        st.metric("Syllables/sec", f"{s.get('speech_syllables_per_sec', 0):.2f}")
        st.metric("Voiced ratio", f"{s.get('voiced_ratio', 0):.2f}")
    else:
        st.info("No speech JSON selected or file missing.")

# ---------- Quick tasks (launchers) ----------
else:
    st.subheader("Quick tasks (launch CLI in this env)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Run webcam app (face_asymmetry.py)**")
        st.caption("Opens a separate OpenCV window. Keys: r=start/stop, c=force-save CSV, s=save avg JSON, q=quit.")
        if st.button("Launch face_asymmetry.py"):
            rc = run_py(["modules/stroke/features/face_asymmetry.py"])
            st.success(f"Exited with code {rc}")

        st.markdown("---")
        st.markdown("**Plot latest CSV → PNG (tools/plot_ai.py)**")
        if st.button("Plot latest CSV"):
            csvs = sorted(LOG_DIR.glob("face_ai_session_*.csv"))
            if csvs:
                latest_csv = str(csvs[-1].resolve())
                rc = run_py(["tools/plot_ai.py", latest_csv])
                st.success(f"Plot script finished (code {rc})")
            else:
                st.warning("No CSV found. Run the webcam first and press **r** then stop.")

    with col2:
        st.markdown("**Record speech (JSON)**")
        device = st.number_input("Input device index", value=0, step=1)
        fs = st.selectbox("Sample rate", [16000, 24000, 32000, 44100, 48000], index=4)
        dur = st.slider("Duration (s)", min_value=3, max_value=15, value=5)
        _agc = st.checkbox("AGC (normalize) + Debug", value=True, help="(UI only; current CLI ignores this)")

        if st.button("Record speech now"):
            args = [
                "modules/stroke/features/speech_rate.py",
                "--device", str(device),
                "--fs", str(fs),
                "--channels", "1",
                "--duration", str(dur),
            ]
            rc = run_py(args)
            st.success(f"Speech recording finished (code {rc}). Reload the Speech tab to view JSON.")

    # 🧩 Add this block below
    st.markdown("---")
    st.subheader("🧪 System Check (Day 9)")
    st.caption("Runs Face + Speech end-to-end and writes a combined status JSON.")

    if st.button("Run system_check_day9.py"):
        rc = run_py(["tools/system_check_day9.py"])
        if rc == 0:
            st.success("✅ System check complete! See data/exports/neuro_system_check_day9.json")
            out_json = EXPORT_DIR / "neuro_system_check_day9.json"
            if out_json.exists():
                st.json(json.load(open(out_json, "r", encoding="utf-8")))
        else:
            st.warning(f"⚠️ system_check_day9.py exited with code {rc}")
