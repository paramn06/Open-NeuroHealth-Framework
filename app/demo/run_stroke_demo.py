from datetime import datetime
import uuid
from onf.sdk.io import save_neuro_unit

# Pretend we computed a face asymmetry score
face_asymmetry = 0.12

neuro_unit = {
    "id": str(uuid.uuid4()),
    "module": "stroke",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "signals": {"face_asymmetry": face_asymmetry},
    "device": "laptop-webcam",
    "notes": "demo run"
}

out_path = save_neuro_unit(neuro_unit, path="data/exports/neuro_unit_demo.json")
print(f"Neuro Unit saved to {out_path}")
