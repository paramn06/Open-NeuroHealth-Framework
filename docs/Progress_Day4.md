# 🧠 Open NeuroHealth Framework — Day 4 Progress

**Date:** 2025-10-26  
**Environment:** `open-neurohealth` (Conda) on Windows

## ✅ What’s working
- Real-time facial landmarks (MediaPipe FaceMesh) from webcam.
- Asymmetry Index (AI) computed per frame using multiple symmetric pairs.
- Session workflow:
  - **r → r**: start/stop logging → CSV saved to `data/logs/face_ai_session_*.csv`
  - **s**: save averaged JSON → `data/exports/neuro_unit_face_ai_avg.json`
  - **q**: quit
- Visualization:
  - `tools/plot_ai.py` plots AI over time, adds color zones, smoothing, and auto-saves PNG to `data/plots/`.

## 🧪 Verification
- Camera probe (`tools/cam_probe.py`) shows working backend on index 0.
- Minimal viewer works; app runs; CSV/JSON/PNG generated and verified.

## 📁 New/Updated files
- `modules/stroke/features/face_asymmetry.py` — live AI + logging + save.
- `tools/cam_probe.py` — backend probe.
- `tools/plot_ai.py` — plotting with smoothing and zones.
- `data/logs/` — per-frame AI CSV (ignored by Git).
- `data/exports/` — averaged Neuro Unit JSON (ignored by Git).
- `data/plots/` — PNG plots (ignored by Git).
- `.gitignore` — ignore data outputs and caches.

## ⚠️ Notes & fixes
- Removed headless OpenCV conflicts; using GUI build (DSHOW primary, MSMF fallback).
- If the app shows no window but viewer works, force the same backend in `run_webcam()`.

## 🎯 Next (Day 5)
- `app/strokeai_demo.py` launcher to run end-to-end.
- `tools/system_check.py` to auto-diagnose env and camera.
- Add basic risk fusion (AI + speech timing prototype).

—  
*Milestone tagged: Day-4 complete ✅*
