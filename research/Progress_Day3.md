# Progress Log – Day 1
- Cloned repo locally and opened in VS Code.
- Created ONF folders (onf/, modules/, apps/, research/, models/, data/, docs/).
- Added schema, SDK saver, and demo runner.
- Next: set up Python env and install OpenCV/MediaPipe for face landmarks.
Completed: repo setup, commits, Git-GitHub integration, ready for .gitignore and dependencies tomorrow.

# Progress Log – Day 2
- Installed Python 3.11 env (onf311)
- Verified dependencies
- Implemented static & webcam asymmetry detection
- Next: average multi-frame AI (Day 3)
# Progress – Day 3 (StrokeAI / ONF)

## What I did
- Ran live face asymmetry demo (MediaPipe + OpenCV).
- Recorded 5–10s session; exported averaged Neuro Unit JSON.
- Verified environment and exported environment.yml (reproducible setup).
- Ensured .gitignore keeps data/exports out of git history.

## Evidence / Artifacts
- JSON: data/exports/neuro_unit_face_ai_avg.json
- Env: environment.yml

## Notes
- AI average looked stable in neutral/smile.
- Next: add CSV session logging + simple plot of AI vs time.


# Progress_Day5.md
✅ Day 5 Summary:
- Completed stable StrokeAI NetLag HUD system.
- Verified FPS tracking, AI symmetry computation, and auto CSV + JSON export.
- Confirmed robust directory handling with absolute paths.
- Ready for stability tests and integration with multi-sensor fusion.
