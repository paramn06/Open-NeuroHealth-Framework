from pathlib import Path
import csv, time
Path("data/logs").mkdir(parents=True, exist_ok=True)
p = f"data/logs/force_test_{time.strftime('%Y%m%d-%H%M%S')}.csv"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t_sec","ai"])
    w.writerows([["0.033","0.0158"],["0.066","0.0161"]])
print("✅ WROTE:", p)
