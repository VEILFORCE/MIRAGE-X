import smtplib
import json
from email.message import EmailMessage

# Load config
with open("config.json", "r") as f:
    config = json.load(f)["email_alerts"]

def send_test_email():
    msg = EmailMessage()
    msg["Subject"] = "🔔 MIRAGE-X Test Alert"
    msg["From"] = config["sender_email"]
    msg["To"] = config["receiver_email"]
    msg.set_content("This is a test alert from your MIRAGE-X intrusion detection system.")

    try:
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

if __name__ == "__main__":
    send_test_email()
