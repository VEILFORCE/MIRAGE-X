import sounddevice as sd
import soundfile as sf

fs = 44100  # Sample rate
seconds = 3  # Duration

print("🎤 Speak now...")
recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32')
sd.wait()

sf.write("test_clip.wav", recording, fs)
print("✅ Saved as test_clip.wav")
