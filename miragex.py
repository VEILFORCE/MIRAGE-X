import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
import datetime
import argparse
import smtplib
import threading
import time
import json
import shutil
import signal
from email.message import EmailMessage
from getpass import getpass

# === Global Flags ===
RUNNING = True
EMAIL_PASSWORD = None
stop_audio_event = threading.Event()

# === Signal Handling ===
def graceful_exit(signum, frame):
    global RUNNING
    if RUNNING:
        print("\n[MIRAGE-X] Gracefully shutting down...")
        RUNNING = False
        stop_audio_event.set()

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

# === Interactive Email Setup ===
def interactive_email_setup():
    config = {
        "email_alerts": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "receiver_email": ""
        }
    }

    enable = input("[MIRAGE-X Setup] Do you want to enable email alerts? (Y/n): ").strip().lower()
    if enable == "n":
        config["email_alerts"]["enabled"] = False
    else:
        config["email_alerts"]["enabled"] = True
        email = input("[MIRAGE-X Setup] Enter your Gmail address to receive alerts: ").strip()
        config["email_alerts"]["sender_email"] = email
        config["email_alerts"]["receiver_email"] = email

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    email_motion = False
    email_audio = False

    if config["email_alerts"]["enabled"]:
        m = input("[MIRAGE-X Setup] Enable motion alerts via email? (Y/n): ").strip().lower()
        a = input("[MIRAGE-X Setup] Enable audio alerts via email? (Y/n): ").strip().lower()
        email_motion = (m != "n")
        email_audio = (a != "n")

    return email_motion, email_audio

# === Email Alert ===
def send_email_alert(subject, body, attachment_path=None):
    global EMAIL_PASSWORD
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        email_conf = config["email_alerts"]
        if not email_conf["enabled"]:
            return

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = email_conf["sender_email"]
        msg["To"] = email_conf["receiver_email"]

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
                maintype, subtype = ("application", "octet-stream")
                if file_name.endswith(".jpg"):
                    maintype, subtype = ("image", "jpeg")
                elif file_name.endswith(".wav"):
                    maintype, subtype = ("audio", "wav")
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
        else:
            if attachment_path:
                print(f"[MIRAGE-X Warning] Attachment not found or empty: {attachment_path}")

        smtp = smtplib.SMTP(email_conf["smtp_server"], email_conf["smtp_port"])
        smtp.starttls()
        smtp.login(email_conf["sender_email"], EMAIL_PASSWORD)
        smtp.send_message(msg)
        smtp.quit()
        print("[MIRAGE-X Email] Alert sent to {}".format(email_conf["receiver_email"]))
    except Exception as e:
        print(f"[MIRAGE-X Email] Failed to send email: {e}")

# === Utilities ===
def cleanup_old_files(folder, days):
    if not os.path.exists(folder):
        return
    cutoff = time.time() - days * 86400
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            os.remove(path)

def enhance_low_light(frame, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(frame, table)

# === Motion Detection ===
def motion_detector(args):
    global RUNNING
    cap = cv2.VideoCapture(0)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    last_motion_time = 0
    cooldown = int(args.cooldown)

    while RUNNING:
        ret, frame2 = cap.read()
        if not ret:
            break

        if args.gamma:
            frame2 = enhance_low_light(frame2, float(args.gamma))

        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours and (time.time() - last_motion_time > cooldown):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"[{timestamp}] Motion detected.")
            snap_path = None
            if args.save_snaps:
                os.makedirs("snapshots", exist_ok=True)
                snap_path = f"snapshots/{timestamp}.jpg"
                cv2.imwrite(snap_path, frame2)
            if args.email_on_motion:
                send_email_alert("MIRAGE-X Alert: Motion Detected", "Motion detected by MIRAGE-X.", snap_path)
            if args.log:
                with open("log.txt", "a") as logf:
                    logf.write(f"[{timestamp}] Motion detected.\n")
            last_motion_time = time.time()

        if not args.headless:
            cv2.imshow("MIRAGE-X", frame2)
            if cv2.waitKey(10) == 27:
                break

        frame1 = frame2
        time.sleep(0.05)

    cap.release()
    cv2.destroyAllWindows()

# === Audio Detection ===
def audio_listener(args):
    last_audio_time = 0
    cooldown = int(args.cooldown)
    sample_rate = 44100

    def callback(indata, frames, time_info, status):
        nonlocal last_audio_time
        if stop_audio_event.is_set():
            raise sd.CallbackStop()

        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > 0.1 and (time.time() - last_audio_time > cooldown):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"[{timestamp}] LOUD SOUND detected! RMS Volume: {volume_norm}")
            audio_path = None
            if args.save_audio:
                os.makedirs("audio_clips", exist_ok=True)
                audio_path = f"audio_clips/{timestamp}.wav"
                sf.write(audio_path, indata, sample_rate)
            if args.email_on_audio:
                send_email_alert("MIRAGE-X Alert: Loud Sound Detected", "Loud audio detected by MIRAGE-X.", audio_path)
            if args.log:
                with open("log.txt", "a") as logf:
                    logf.write(f"[{timestamp}] Loud audio detected.\n")
            last_audio_time = time.time()

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            while not stop_audio_event.is_set():
                time.sleep(0.1)
    except Exception as e:
        print(f"[MIRAGE-X Audio] Audio stream closed: {e}")

# === Main ===
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MIRAGE-X: Motion & Audio Intrusion Detection System")
    parser.add_argument("--headless", action="store_true", help="Run without showing camera feed")
    parser.add_argument("--cooldown", default=5, help="Cooldown time (sec) between alerts")
    parser.add_argument("--gamma", type=float, help="Gamma correction for low-light enhancement")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio detection")
    parser.add_argument("--no-video", action="store_true", help="Disable motion detection")
    parser.add_argument("--save-audio", action="store_true", help="Save audio recordings")
    parser.add_argument("--save-snaps", action="store_true", help="Save motion snapshots")
    parser.add_argument("--log", action="store_true", help="Log events to file")
    parser.add_argument("--cleanup-days", type=int, help="Auto-delete logs older than N days")
    args = parser.parse_args()

    args.email_on_motion, args.email_on_audio = interactive_email_setup()

    with open("config.json", "r") as f:
        config = json.load(f)
    if config["email_alerts"]["enabled"]:
        EMAIL_PASSWORD = getpass("[MIRAGE-X] Enter your 16-char Gmail App Password: ")

    if args.cleanup_days:
        cleanup_old_files("snapshots", args.cleanup_days)
        cleanup_old_files("audio_clips", args.cleanup_days)

    if not args.no_audio:
        print("[MIRAGE-X] Audio detection started...")
        threading.Thread(target=audio_listener, args=(args,), daemon=True).start()

    if not args.no_video:
        print("[MIRAGE-X] Motion detection started.")
        motion_detector(args)

    print("[MIRAGE-X] Shutting down.")

