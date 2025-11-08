# ⚡ SynFAST  
### Rapid Neuro-AI Stroke Detection System  
*A module of the Open-NeuroHealth Framework by NeuroSynTech Labs*

---

## 🧠 Overview

**SynFAST** (Synergic Fast-Acting Neuro AI System) is a lightweight, on-device prototype designed for **real-time stroke detection** using multimodal analysis — **facial asymmetry**, **speech clarity**, and **response dynamics**.

Developed as part of the **Open-NeuroHealth Framework**, SynFAST aims to make **early neurological assessment** accessible, fast, and privacy-preserving.

---

## 🚀 Key Features

- ⚡ **Real-time facial analysis** — detects subtle asymmetry linked to early stroke signs  
- 🗣️ **Speech clarity & rate assessment** — identifies dysarthria patterns  
- 🔁 **Modular NeuroSyn pipeline** — integrates face + speech modules in a unified dashboard  
- ☁️ **Streamlit-based UI** — simple, interactive, and deployable via cloud or local device  
- 🔒 **Privacy-first** — all data processed locally (no external API dependencies)

---

## 🧩 System Architecture

Input (Camera / Mic)
│
▼
[Face Module] → Facial Asymmetry Index
[Speech Module] → Clarity / Rate Metrics
│
▼
[Fusion Engine]
│
▼
Streamlit Dashboard
│
▼
Output: Stroke Likelihood + Logs

yaml
Copy code

---

## 🧪 Tech Stack

| Component | Technology |
|------------|-------------|
| UI / Visualization | Streamlit |
| AI / CV | OpenCV, Mediapipe, Numpy |
| Audio Analysis | Librosa / SpeechRecognition |
| Environment | Python 3.10+ |
| Hosting | Streamlit Cloud |
| Domain | [https://synfast.neurohealthlabs.in](https://synfast.neurohealthlabs.in) |

---

## ⚙️ Quickstart (Local)

```bash
# 1️⃣ Clone the repository
git clone https://github.com/paramn06/Open-NeuroHealth-Framework.git
cd Open-NeuroHealth-Framework

# 2️⃣ Create a conda environment
conda create -n open-neurohealth python=3.10 -y
conda activate open-neurohealth

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Launch the SynFAST dashboard
streamlit run app/onf_dashboard.py
☁️ Deployment
This project is deployed via Streamlit Cloud
🔗 Live Prototype: strokeneurosyn.streamlit.app
🌐 Custom Domain: synfast.neurohealthlabs.in

🧠 Research Context
SynFAST is a functional prototype (TRL-4) built within the Open-NeuroHealth initiative —
a modular, open-science framework for building interoperable neuro-AI systems.

This work contributes to:

Accessible stroke screening for low-resource settings

Integration of biobehavioral biomarkers (face, speech, response)

Laying the foundation for TRL-5 validation & real-world testing

📈 Current TRL Status
Phase	Goal	Status
TRL 3	Module-level integration	✅ Complete
TRL 4	Functional prototype	✅ Complete
TRL 5	Validation & limited user testing	🔄 In progress

🧩 Project Structure
bash
Copy code
Open-NeuroHealth-Framework/
│
├── app/
│   ├── onf_dashboard.py          # Streamlit dashboard (SynFAST)
│   ├── face_module.py
│   ├── speech_module.py
│   └── utils/
│
├── modules/
│   └── stroke/features/
│
├── tools/
│   └── system_check.py
│
├── docs/
│   └── TRL4_Validation_Report.md
│
├── data/
│   └── logs/
│
├── requirements.txt
└── README.md
⚖️ Licensing & Attribution
© 2025 NeuroSynTech / Open-NeuroHealth Framework
All rights reserved.
This prototype is released for academic and research collaboration purposes.

Do not use for clinical diagnosis without regulatory validation.

💬 Contact
Developer: Parameshwar P.
Institution: Amrita School of Biotechnology
Email: contact@neurohealthlabs.in
Website: https://neurohealthlabs.in

SynFAST — Detect faster. Act sooner. ⚡
Built under the Open-NeuroHealth Framework for the NeuroSynTech Initiative.

