# -------------------------------------------------------------
#  Open NeuroHealth Framework © 2025 Parameshwar
#  Author: Parameshwar  |  Version: 1.0 (Day 7 Build)
#  Licensed under the MIT License
#  This software is an original work developed for
#  neuro-diagnostic and research awareness applications.
# -------------------------------------------------------------
from pathlib import Path
import csv, time
Path("data/logs").mkdir(parents=True, exist_ok=True)
p = f"data/logs/force_test_{time.strftime('%Y%m%d-%H%M%S')}.csv"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t_sec","ai"])
    w.writerows([["0.033","0.0158"],["0.066","0.0161"]])
print("✅ WROTE:", p)
