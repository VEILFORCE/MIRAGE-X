# email_alert.py
import smtplib
import ssl
import json
from email.message import EmailMessage
from pathlib import Path

def load_config():
    config_path = Path("config.json")
    if not config_path.exists():
        print("[!] config.json not found. Email alerts disabled.")
        return None
    with open(config_path, "r") as file:
        return json.load(file).get("email_alerts")

def send_email(subject, body, attachments=[]):
    config = load_config()
    if not config or not config.get("enabled"):
        return

    try:
        msg = EmailMessage()
        msg["From"] = config["sender_email"]
        msg["To"] = config["receiver_email"]
        msg["Subject"] = subject
        msg.set_content(body)

        for file_path in attachments:
            file_path = Path(file_path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    data = f.read()
                    msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=file_path.name)

        context = ssl.create_default_context()
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls(context=context)
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)

        print("[MIRAGE-X Email] Alert email sent.")

    except Exception as e:
        print(f"[MIRAGE-X Email] Failed to send email: {e}")
