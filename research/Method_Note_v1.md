# Method Note v1 – Facial Asymmetry Prototype

## Objective
To detect early neurological asymmetry via smartphone camera using face landmarks.

## Tools
- OpenCV / MediaPipe
- Python 3.10
- Sample volunteer data (healthy adults)

## Plan
1. Capture short (5s) videos of smiling and speaking.
2. Extract left-right facial ratios using landmark detection.
3. Calculate Asymmetry Index (AI) = |Left - Right| / (Left + Right).
4. Validate repeatability across 10 volunteers.

## Next Step
Implement pilot module under `/app/` in coming weeks.
