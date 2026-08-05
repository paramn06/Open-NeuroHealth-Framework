import os, json, glob, subprocess, sys, math
import cv2
import numpy as np
from pathlib import Path
import pandas as pd
import streamlit as st

# ---------- WebRTC Cloud Video Imports ----------
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration
import mediapipe as mp

# ---------- Force UTF-8 for Windows ----------
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

# ---------- Paths (auto-detected) ----------
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
        ["Live Scanner (WebRTC)", "Face (CSV/JSON viewer)", "Speech (JSON viewer)", "Quick tasks"],
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
    """Run a Python script reliably."""
    script = Path(args_list[0])
    if not script.is_absolute():
        script = (REPO / script).resolve()

    cmd = [sys.executable, str(script)] + [str(a) for a in args_list[1:]]

    st.write("```")
    st.write(f"📁 Repo: {REPO}")
    st.write(f"▶️  Command: {cmd}")
    st.write("```")

    try:
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        env.setdefault("PYTHONUTF8", "1")

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        assert proc.stdout is not None
        for line in proc.stdout:
            st.write(line.rstrip())
        proc.wait()

        if proc.returncode == 0:
            st.success("✅ Process finished successfully")
        else:
            st.warning(f"⚠️ Process exited with code {proc.returncode}")
        return proc.returncode

    except FileNotFoundError as e:
        st.error(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        st.error(f"💥 Unexpected error: {e}")
        return 1

# ---------- WebRTC Cloud Face Scanner ----------
if tab == "Live Scanner (WebRTC)":
    st.subheader("🌐 Cloud-Ready Live Facial Asymmetry Scanner")
    st.write("This module runs securely in your browser and works on mobile devices without crashing the Streamlit Cloud server.")
    
    RTC_CONFIGURATION = RTCConfiguration(
        {
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302",
                        "stun:stun1.l.google.com:19302",
                        "stun:stun2.l.google.com:19302",
                        "stun:stun3.l.google.com:19302",
                        "stun:global.stun.twilio.com:3478",
                    ]
                }
            ]
        }
    )

    class FaceAsymmetryProcessor(VideoTransformerBase):
        def __init__(self):
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.pairs = [(61, 291), (133, 362), (33, 263)]
            self.L_EYE_OUT, self.R_EYE_OUT = 33, 263

        def _pt_nan(self, landmarks, idx, w, h):
            try:
                lm = landmarks[idx]
                return float(lm.x * w), float(lm.y * h)
            except Exception:
                return float("nan"), float("nan")

        def transform(self, frame):
            try:
                img = frame.to_ndarray(format="bgr24")
                h, w = img.shape[:2]
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(img_rgb)

                if results.multi_face_landmarks:
                    for fl in results.multi_face_landmarks:
                        mp.solutions.drawing_utils.draw_landmarks(
                            img, fl, mp.solutions.face_mesh.FACEMESH_TESSELATION,
                            connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)
                        )
                        
                        lx, ly = self._pt_nan(fl.landmark, self.L_EYE_OUT, w, h)
                        rx, ry = self._pt_nan(fl.landmark, self.R_EYE_OUT, w, h)
                        
                        if not (math.isnan(lx) or math.isnan(rx)):
                            iod = float(math.hypot(rx - lx, ry - ly)) + 1e-6
                            diffs = []
                            for L_idx, R_idx in self.pairs:
                                _Lx, Ly = self._pt_nan(fl.landmark, L_idx, w, h)
                                _Rx, Ry = self._pt_nan(fl.landmark, R_idx, w, h)
                                if not (math.isnan(Ly) or math.isnan(Ry)):
                                    L_vert = abs(Ly - ly) / iod
                                    R_vert = abs(Ry - ry) / iod
                                    diffs.append(abs(L_vert - R_vert))
                            
                            ai = float(np.mean(diffs)) if diffs else 1.0
                            cv2.putText(img, f"AI Asymmetry Score: {ai:.3f}", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(img, "Face not detected", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                return img
            except Exception:
                return frame.to_ndarray(format="bgr24")

    webrtc_streamer(
        key="stroke-face-scanner-live",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=FaceAsymmetryProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

# ---------- Face viewer ----------
elif tab == "Face (CSV/JSON viewer)":
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
        chosen_csv_path = None

        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
            if getattr(uploaded_csv, "name", None):
                chosen_csv_path = Path(uploaded_csv.name)
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
            st.info("No averaged JSON found yet.")

        st.markdown("---")
        st.subheader("Saved Plot (PNG)")

        plots_dir = (REPO / "data" / "plots")
        plots_dir.mkdir(parents=True, exist_ok=True)

        png_guess = None
        if chosen_csv_path is not None:
            png_guess = (plots_dir / (chosen_csv_path.stem + ".png")).resolve()

        c1, c2 = st.columns(2)
        with c1:
            regen = st.button("Generate plot for this CSV")
        with c2:
            show_latest = st.button("Show latest plot in folder")

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

# ---------- Quick tasks ----------
else:
    st.subheader("Quick tasks (launch CLI in this env)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Run webcam app (face_asymmetry.py) - LOCAL ONLY**")
        st.caption("WARNING: This will crash on Streamlit Cloud. Use the WebRTC tab instead.")
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
                st.warning("No CSV found.")

    with col2:
        st.markdown("**Record speech (JSON)**")
        device = st.number_input("Input device index", value=0, step=1)
        fs = st.selectbox("Sample rate", [16000, 24000, 32000, 44100, 48000], index=4)
        dur = st.slider("Duration (s)", min_value=3, max_value=15, value=5)

        if st.button("Record speech now"):
            args = [
                "modules/stroke/features/speech_rate.py",
                "--device", str(device),
                "--fs", str(fs),
                "--channels", "1",
                "--duration", str(dur),
            ]
            rc = run_py(args)
            st.success(f"Speech recording finished (code {rc}).")

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
