# send_raw.py

import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import math
import random
import matplotlib.pyplot as plt

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://beatai-bc460-default-rtdb.firebaseio.com/'
})

def generate_ecg_signal(sample_rate=40, duration_sec=10, bpm=90):
    """
    Generates a simulated ECG signal with a normal sinus rhythm.
    
    - sample_rate: number of samples per second.
    - duration_sec: total duration of signal in seconds.
    - bpm: target heart rate.
    
    Returns a noisy ECG signal as a NumPy array.
    """
    n_samples = sample_rate * duration_sec  # e.g., 400 samples
    beats_per_sec = bpm / 60.0               # e.g., 90/60 = 1.5 beats per second
    total_beats = int(beats_per_sec * duration_sec)  # 15 beats in 10 sec
    beat_length = int(round(n_samples / total_beats))  # approx. 400/15 ≈ 27 samples per beat

    # Generate one beat template using Gaussian curves for P, QRS, and T waves:
    t = np.linspace(0, 1, beat_length)
    # P wave: small bump at t ~ 0.2
    p_wave = 0.1 * np.exp(-((t - 0.2) ** 2) / (2 * 0.01))
    # QRS complex: sharp spike at t ~ 0.5
    qrs = 0.8 * np.exp(-((t - 0.5) ** 2) / (2 * 0.0004))
    # T wave: broader bump at t ~ 0.75
    t_wave = 0.2 * np.exp(-((t - 0.75) ** 2) / (2 * 0.0049))
    beat = p_wave + qrs + t_wave + 1.0  # baseline at 1.0
    
    # Repeat the beat to cover the whole duration
    ecg_signal = np.tile(beat, total_beats)
    # Trim or pad to exactly n_samples
    ecg_signal = ecg_signal[:n_samples]
    # Add Gaussian noise (e.g., standard deviation 0.02)
    noise = np.random.normal(0, 0.02, size=ecg_signal.shape)
    ecg_signal_noisy = ecg_signal + noise
    return ecg_signal_noisy

# Parameters
sample_rate = 40  # samples per second
duration_sec = 10
n_samples = sample_rate * duration_sec

# Generate the simulated ECG signal (400 samples)
ecg_signal = generate_ecg_signal(sample_rate, duration_sec, bpm=90)
timestamps = np.arange(n_samples) * (1000 / sample_rate)  # in ms (25ms intervals)

# Plot the simulated ECG signal
plt.figure(figsize=(10, 4))
plt.plot(timestamps, ecg_signal, marker='o', linestyle='-', markersize=2)
plt.title("Simulated ECG Signal (10s, ~90 BPM with noise)")
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.show()

# Prepare JSON data: list of dictionaries with "v" (voltage) and "t" (timestamp)
ecg_data = []
for i in range(n_samples):
    ecg_data.append({"v": round(float(ecg_signal[i]), 3), "t": int(timestamps[i])})

# Push the JSON array to Firebase at heart_risk/session/raw_data
ref = db.reference("heart_risk/session/raw_data")
ref.set(ecg_data)

print("✅ Sent simulated ECG data (400 samples) to Firebase under 'raw_data'")