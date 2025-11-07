# app/onf_dashboard.py
import os, json, glob, subprocess, sys
from pathlib import Path
import pandas as pd
import streamlit as st

REPO = Path(r"C:\Users\MY BOOK\Open-NeuroHealth-Framework")
LOG_DIR = REPO / "data" / "logs"
EXPORT_DIR = REPO / "data" / "exports"

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
    st.caption("Tip: generate data via the CLI first (camera/mic).")

# --- Helpers ---
def latest(pattern: str):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None

def run_py(args_list):
    """Run a python module/script in the ONF env and stream output."""
    st.write("```")
    try:
        proc = subprocess.Popen(
            [sys.executable] + args_list,
            cwd=str(REPO),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            st.write(line.rstrip())
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.write(f"[ERROR] {e}")
        return 1
    finally:
        st.write("```")

# --- Face viewer ---
if tab == "Face (CSV/JSON viewer)":
    st.subheader("Face Asymmetry Sessions (CSV)")
    col1, col2 = st.columns(2)

    with col1:
        # Pick a CSV (auto-select latest)
        csv_files = sorted(LOG_DIR.glob("face_ai_session_*.csv"))
        sel_csv = st.selectbox(
            "Choose a CSV session", [f.name for f in csv_files],
            index=(len(csv_files)-1) if csv_files else None
        )
        uploaded_csv = st.file_uploader("...or upload a CSV", type=["csv"], key="face_csv_up")

        df = None
        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
        elif sel_csv:
            df = pd.read_csv(LOG_DIR / sel_csv)

        if df is not None and not df.empty:
            st.dataframe(df.head(50), use_container_width=True)
            st.line_chart(df.set_index("t_sec")["ai"], use_container_width=True)
        else:
            st.info("No CSV selected or file is empty.")

    with col2:
        st.subheader("Averaged JSON (latest)")
        latest_json = latest(str(EXPORT_DIR / "neuro_unit_face_ai_avg.json"))
        if latest_json and os.path.isfile(latest_json):
            j = json.load(open(latest_json, "r", encoding="utf-8"))
            st.json(j)
        else:
            st.info("No averaged JSON found yet. Press **r** then **s** in the webcam app to generate one.")

# --- Speech viewer ---
elif tab == "Speech (JSON viewer)":
    st.subheader("Speech Neuro Unit (JSON)")
    # Pick or upload speech JSON
    json_files = sorted(EXPORT_DIR.glob("neuro_unit_speech_rate*.json"))
    sel_json = st.selectbox(
        "Choose a speech JSON", [f.name for f in json_files],
        index=(len(json_files)-1) if json_files else None
    )
    uploaded_json = st.file_uploader("...or upload a JSON", type=["json"], key="speech_json_up")

    js = None
    if uploaded_json is not None:
        js = json.load(uploaded_json)
    elif sel_json:
        js = json.load(open(EXPORT_DIR / sel_json, "r", encoding="utf-8"))

    if js:
        st.json(js)
        s = js.get("signals", {})
        st.metric("Syllables/sec", f"{s.get('speech_syllables_per_sec', 0):.2f}")
        st.metric("Voiced ratio", f"{s.get('voiced_ratio', 0):.2f}")
    else:
        st.info("No speech JSON selected or file missing.")

# --- Quick tasks (launchers) ---
else:
    st.subheader("Quick tasks (launch CLI in this env)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Run: Face webcam app (CSV/JSON)**")
        st.caption("Window opens separately. Keys: r=start/stop, s=save avg JSON, q=quit")
        if st.button("Launch face_asymmetry.py"):
            rc = run_py(["modules/stroke/features/face_asymmetry.py"])
            st.success(f"Exited with code {rc}")

        st.markdown("---")
        st.markdown("**Plot latest CSV (CLI)**")
        if st.button("Plot latest CSV"):
            latest_csv = latest(str(LOG_DIR / "face_ai_session_*.csv"))
            if latest_csv:
                rc = run_py(["tools/plot_ai.py", latest_csv])
                st.success(f"Plot script finished (code {rc})")
            else:
                st.warning("No CSV found. Run the webcam first and press **r** then **c**/**stop**.")

    with col2:
        st.markdown("**Record speech (JSON)**")
        device = st.number_input("Input device index", value=9, step=1)
        fs = st.selectbox("Sample rate", [16000, 24000, 32000, 44100, 48000], index=4)
        dur = st.slider("Duration (s)", min_value=3, max_value=15, value=5)
        agc = st.checkbox("AGC (normalize) + Debug", value=True)

        if st.button("Record speech now"):
            args = ["modules/stroke/features/speech_rate.py",
                    "--device", str(device), "--fs", str(fs),
                    "--channels", "1", "--duration", str(dur)]
            if agc:
                args += ["--agc", "--debug"]
            rc = run_py(args)
            st.success(f"Speech recording finished (code {rc}). Reload Speech tab to view JSON.")
