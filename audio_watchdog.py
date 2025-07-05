import sounddevice as sd
import numpy as np
import soundfile as sf
import datetime
import os
import argparse

# ────── CLI Options ──────
parser = argparse.ArgumentParser(description="MIRAGE-X Audio Anomaly Detector")
parser.add_argument("--speak", action="store_true", help="Enable voice alerts")
args = parser.parse_args()

# ────── Directories ──────
LOG_DIR = "logs"
AUDIO_CLIP_DIR = "audio_clips"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AUDIO_CLIP_DIR, exist_ok=True)

# ────── Audio Settings ──────
THRESHOLD = 0.1            # Sensitivity (lower = more sensitive)
DURATION = 1               # Duration to check for anomaly (in seconds)
AUDIO_CLIP_DURATION = 5    # Save 5 sec audio clip after anomaly
SAMPLERATE = 44100         # Sample rate for recording

# ────── Voice Engine ──────
if args.speak:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)

print("[MIRAGE-X Audio] Listening for anomalies... Press Ctrl+C to stop.")

# ────── Event Logger ──────
def log_event(volume):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_msg = f"[{timestamp}] LOUD SOUND detected! RMS Volume: {volume:.3f}"
    
    print(log_msg)
    with open(os.path.join(LOG_DIR, "audio_log.txt"), "a") as f:
        f.write(log_msg + "\n")

    # Save audio clip
    clip_file = os.path.abspath(os.path.join(AUDIO_CLIP_DIR, f"{timestamp}.wav"))

    print(f"[MIRAGE-X Audio] Saving clip: {clip_file}")
    clip = sd.rec(int(AUDIO_CLIP_DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype='float32')
    sd.wait()
    sf.write(clip_file, clip, SAMPLERATE)

    # Optional voice alert
    if args.speak:
        alert_message = f"Warning. Loud sound detected. Volume {volume:.2f}"
        engine.say(alert_message)
        engine.runAndWait()

# ────── Monitoring Loop ──────
try:
    while True:
        recording = sd.rec(int(DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype='float64')
        sd.wait()
        rms = np.sqrt(np.mean(recording**2))

        if rms > THRESHOLD:
            log_event(rms)

except KeyboardInterrupt:
    print("\n[MIRAGE-X Audio] Monitoring stopped.")

