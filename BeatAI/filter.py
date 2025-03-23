import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt

# Initialize Firebase (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://beatai-bc460-default-rtdb.firebaseio.com/'
    })

def calculate_bpm(ecg_data, sample_rate=40, refractory_period=10):
    """
    Calculate BPM using local maximum detection:
      - ecg_data: list of dicts, each with "v" and "t"
      - sample_rate: samples per second (40 Hz)
      - refractory_period: number of samples to skip after detecting a peak
    
    The function detects a peak if the voltage is a local maximum and exceeds a threshold.
    It then multiplies the number of peaks in 10 seconds by 6 to get BPM.
    """
    voltages = [float(d["voltage"]) for d in ecg_data]
    times = [float(d["time"]) for d in ecg_data]
    
    # Set a threshold that only the QRS peaks should exceed.
    # With our simulated signal, QRS peaks are near 1.8 V so we use 1.3 as threshold.
    threshold = 2.4  # 1.65 V
    peaks = []
    i = 1
    while i < len(voltages) - 1:
        # Check if current sample is a local maximum above the threshold
        if voltages[i] > voltages[i-1] and voltages[i] > voltages[i+1] and voltages[i] >= threshold:
            peaks.append(i)
            i += refractory_period  # Skip ahead to avoid double-counting the same peak
        else:
            i += 1
    # For data covering 10 seconds, BPM = (# of peaks) * 6
    bpm = len(peaks) * 6
    
    return bpm

def main():
    ref = db.reference("heart_risk/session")
    raw_data = ref.child("raw_data").get()
    
    if not raw_data or len(raw_data) == 0:
        print("⚠️ No raw ECG data found in 'raw_data'.")
        return
    
    bpm = calculate_bpm(raw_data, sample_rate=40, refractory_period=10)
    
    # Write the calculated BPM to Firebase under heart_rate (no timestamp needed)
    ref.child("heart_rate").update({"BPM": bpm})
    print(f"✅ BPM calculated and stored: {bpm} BPM")

if __name__ == "__main__":
    main()
