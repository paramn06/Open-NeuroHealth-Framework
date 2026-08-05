# Add repo root to sys.path so imports like modules.stroke.* work when run from app/
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# app/triage_screen.py
import streamlit as st # type: ignore
import json
import datetime
import io
import os

st.set_page_config(page_title="ONF — Stroke Triage", layout="wide")

st.title("Open NeuroHealth — Stroke Triage (Prototype)")

# Attempt to import your modules; fallback gracefully if missing
def safe_import(module_path, attr=None):
    try:
        module = __import__(module_path, fromlist=["*"])
        return getattr(module, attr) if attr and hasattr(module, attr) else module
    except Exception as e:
        return None

# Try common module entrypoints you have
face_module = safe_import("modules.stroke.features.face_asymmetry")
face_image_module = safe_import("modules.stroke.features.face_ai_image")
speech_module = safe_import("modules.stroke.features.speech_rate")
fusion_simple = safe_import("modules.stroke.fusion.simple_fusion")
fusion_face_speech = safe_import("modules.stroke.fusion.fuse_face_speech")

# UI: intake
with st.sidebar:
    st.header("Session")
    name = st.text_input("Patient / Subject name (optional)")
    anonymize = st.checkbox("Anonymize export (recommended)", value=True)
    notes = st.text_area("Notes (short)")

st.header("Capture inputs")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Face / Video")
    uploaded_image = st.file_uploader("Upload face image (or camera capture)", type=["png","jpg","jpeg"])
    run_face = st.button("Analyze Face")

with col2:
    st.subheader("Speech / Audio")
    uploaded_audio = st.file_uploader("Upload audio (wav/mp3)", type=["wav","mp3","m4a"], key="audio_upload")
    run_speech = st.button("Analyze Speech")

# Results placeholders
face_result = {"status": "not run"}
speech_result = {"status": "not run"}
fusion_result = {"status": "not run"}

# ---- REPLACE Face processing block with this ----
if run_face:
    st.info("DEBUG: run_face clicked")
    if not uploaded_image:
        st.warning("No image uploaded — please upload a JPG/PNG and try again.")
    else:
        try:
            st.write("DEBUG: reading uploaded image bytes (len)", len(uploaded_image.read()))
            uploaded_image.seek(0)
            image_bytes = uploaded_image.read()
            # write a temp file so you can inspect it
            tmp_path = "data/debug_face_input.jpg"
            os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
            with open(tmp_path, "wb") as f:
                f.write(image_bytes)
            st.write(f"Saved uploaded image to {tmp_path}")

            # try several import / function names and log outcomes
            if face_image_module:
                st.write("DEBUG: face_image_module exists:", getattr(face_image_module, "__name__", str(face_image_module)))
            else:
                st.write("DEBUG: face_image_module NOT FOUND")

            if face_module:
                st.write("DEBUG: face_module exists:", getattr(face_module, "__name__", str(face_module)))
            else:
                st.write("DEBUG: face_module NOT FOUND")

            # Try known function names
            used = False
            # 1) process_image_bytes -> then face_module.analyze_face
            try:
                if face_image_module and hasattr(face_image_module, "process_image_bytes"):
                    st.write("DEBUG: calling face_image_module.process_image_bytes(...)")
                    processed = face_image_module.process_image_bytes(image_bytes)
                    st.write("DEBUG: processed type:", type(processed))
                    if face_module and hasattr(face_module, "analyze_face"):
                        st.write("DEBUG: calling face_module.analyze_face(processed)")
                        face_result = face_module.analyze_face(processed)
                        used = True
            except Exception as e:
                st.write("DEBUG: process_image_bytes -> analyze_face failed:", repr(e))

            # 2) analyze_face_from_bytes
            if not used:
                try:
                    if face_module and hasattr(face_module, "analyze_face_from_bytes"):
                        st.write("DEBUG: calling face_module.analyze_face_from_bytes(...)")
                        face_result = face_module.analyze_face_from_bytes(image_bytes)
                        used = True
                except Exception as e:
                    st.write("DEBUG: analyze_face_from_bytes failed:", repr(e))

            # 3) analyze_face (raw bytes) fallback
            if not used:
                try:
                    if face_module and hasattr(face_module, "analyze_face"):
                        st.write("DEBUG: calling face_module.analyze_face with bytes")
                        face_result = face_module.analyze_face(image_bytes)
                        used = True
                except Exception as e:
                    st.write("DEBUG: analyze_face(bytes) failed:", repr(e))

            # 4) last fallback: basic message
            if not used:
                st.warning("DEBUG: No suitable face function found. Returning placeholder.")
                face_result = {"face_summary": "no-face-function", "debug": True}

            st.success("Face analysis result:")
            st.json(face_result)
        except Exception as e:
            st.error("UNCAUGHT face processing error:")
            st.exception(e)

# ---- REPLACE Speech processing block with this ----
if run_speech:
    st.info("DEBUG: run_speech clicked")
    if not uploaded_audio:
        st.warning("No audio uploaded — please upload a WAV/MP3 file and try again.")
    else:
        try:
            uploaded_audio.seek(0)
            audio_bytes = uploaded_audio.read()
            st.write("DEBUG: read audio bytes len:", len(audio_bytes))
            tmp_audio = "data/debug_audio_input.wav"
            os.makedirs(os.path.dirname(tmp_audio), exist_ok=True)
            with open(tmp_audio, "wb") as f:
                f.write(audio_bytes)
            st.write(f"Saved audio to {tmp_audio}")

            used = False
            # Try likely function names
            try:
                if speech_module and hasattr(speech_module, "extract_speech_rate"):
                    st.write("DEBUG: calling speech_module.extract_speech_rate")
                    speech_result = speech_module.extract_speech_rate(io.BytesIO(audio_bytes))
                    used = True
            except Exception as e:
                st.write("DEBUG: extract_speech_rate failed:", repr(e))

            if not used:
                try:
                    if speech_module and hasattr(speech_module, "process_audio_bytes"):
                        st.write("DEBUG: calling speech_module.process_audio_bytes")
                        speech_result = speech_module.process_audio_bytes(audio_bytes)
                        used = True
                except Exception as e:
                    st.write("DEBUG: process_audio_bytes failed:", repr(e))

            if not used:
                st.warning("DEBUG: No speech function found — returning placeholder.")
                speech_result = {"speech_summary": "no-speech-function", "debug": True}

            st.success("Speech analysis result:")
            st.json(speech_result)
        except Exception as e:
            st.error("UNCAUGHT speech processing error:")
            st.exception(e)

# Fusion / triage
if (face_result.get("face_summary") or face_result.get("score")) or (speech_result.get("speech_summary") or speech_result.get("rate")):
    st.subheader("Fusion / Triage")
    try:
        # try simple fusion first
        if fusion_simple and hasattr(fusion_simple, "fuse"):
            fusion_result = fusion_simple.fuse(face_result, speech_result)
        elif fusion_face_speech and hasattr(fusion_face_speech, "fuse"):
            fusion_result = fusion_face_speech.fuse(face_result, speech_result)
        else:
            # basic rule-based fallback
            score = 0
            if isinstance(face_result, dict):
                face_text = json.dumps(face_result).lower()
                score_val = face_result.get("score", 0)
                try:
                    score_num = float(score_val)
                except (TypeError, ValueError):
                    score_num = 0.0
                if "asymmetry" in face_text or score_num > 0.5:
                    score += 1
            if isinstance(speech_result, dict):
                # safely interpret rate as a float if possible
                rate_val = speech_result.get("rate", 0)
                try:
                    rate_num = float(rate_val)
                except (TypeError, ValueError):
                    rate_num = 0.0
                if "slow" in json.dumps(speech_result).lower() or rate_num < 2.0:
                    score += 1
            if score >= 1:
                fusion_result = {"triage": "Possible stroke", "score": score}
            else:
                fusion_result = {"triage": "Unlikely stroke", "score": score}
        st.write(fusion_result)
    except Exception as e:
        st.error(f"Fusion error: {e}")

# Export / Save
st.markdown("---")
st.subheader("Save / Export session")
if st.button("Export JSON"):
    session = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "name": None if anonymize else name,
        "notes": notes,
        "face_result": face_result,
        "speech_result": speech_result,
        "fusion_result": fusion_result
    }
    out = json.dumps(session, indent=2)
    st.download_button("Download session JSON", out, file_name=f"session_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json", mime="application/json")
    st.success("Session prepared for download")

st.caption("Prototype: for research only. Not a clinical diagnostic device.")
