<<<<<<< HEAD
# MIRAGE-X
🎭 MIRAGE-X – A stealth-grade motion and audio surveillance tool for local anomaly detection.
=======
# 🎭 MIRAGE-X

**MIRAGE-X** is a stealth-grade motion and audio anomaly detection system built for local surveillance and intrusion logging. Designed for privacy-conscious users, cybersecurity professionals, and red team operatives, MIRAGE-X operates silently — logging movement, detecting sound, and optionally alerting you via email.

> Developed under **[VEILFORCE](https://github.com/veilforce)** — tools engineered for digital and physical security.

---

## 🔥 Features

- 📸 **Motion Detection** using webcam feed
- 🔊 **Audio Anomaly Detection** via mic (RMS threshold based)
- 📩 **Email Alerts** (with optional image/audio attachments)
- 💾 **Snapshot and Audio Logging**
- 🧠 **Low-light enhancement** (gamma correction)
- 🕶️ **Headless Mode** for silent background monitoring
- 🗂️ **Log cleanup** automation
- 🔐 **Password-protected alert setup**


---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/veilforce/miragex.git
cd miragex

2. Set up the Environment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

3. Run MIRAGE-X example usage:

python3 miragex.py --headless --save-snaps --save-audio --log --cooldown 10

You will be interactively prompted to set up email alerts. We recommend using a Gmail App Password.

⚙️ First Run Setup: Email Alerts
On your first run, MIRAGE-X will prompt you to set up email alerts. Based on your responses, it will automatically generate a config.json file storing your preferences.

📄 config.json will look like:

json

{
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "receiver_email": "your-email@gmail.com"
  }
}

🔑 Your Gmail App Password (16 characters) is entered at runtime only — it is never saved to disk.

To disable or change email preferences, just delete config.json and restart the tool.

⚙️ Command-Line Options
Flag	Description
--headless	Run silently without camera window
--cooldown N	Delay (in sec) between repeated alerts
--gamma 1.5	Apply low-light correction
--save-snaps	Save webcam images on motion
--save-audio	Save mic recordings on sound
--log	Log events to log.txt
--cleanup-days N	Auto-delete old logs/snaps
--no-video	Disable webcam/motion detection
--no-audio	Disable mic/audio anomaly detection

📂 File Structure

miragex/
├── miragex.py          # Main tool
├── requirements.txt    # Dependencies
├── config.json         # Email config (auto-generated)
├── log.txt             # Logs (if enabled)
├── snapshots/          # Saved images
└── audio_clips/        # Saved audio files


🛡️ Security & Ethics
MIRAGE-X is intended for ethical use only — personal safety, physical intrusion detection, and authorized surveillance. Misuse is your responsibility.

🧠 About VEILFORCE
VEILFORCE is an independent cyberware lab crafting stealth tools and tactical software for privacy, red teaming, and physical security.

🌐 https://github.com/VEILFORCE
📷 Instagram: @lucienrosei
🐦 Twitter/X: @lucienrosei



🛡️ License
This project is licensed under the MIT License. See LICENSE for more information.

🤖 AI Assistance Attribution
This project was partially assisted by AI systems, including help with code refactoring, security strategies, content generation, and automation logic.
All final decisions, testing, and operational controls were implemented manually.


>>>>>>> 9f62717 (🚀 First full push: MIRAGE-X v1.0 released)
