import json
import matplotlib.pyplot as plt

    # Load the exported JSON file from Firebase
    # with open("beatai-bc460-default-rtdb-export.json", "r") as f:
    #     data = json.load(f)
data = json_file
    # Extract the raw_data list from the session node
raw_data = data["heart_risk"]["session"]["raw_data"]

    # Extract time and voltage values into separate lists
times = [entry["time"] for entry in raw_data]
voltages = [entry["voltage"] for entry in raw_data]

    # Plot the waveform
plt.figure(figsize=(12, 6))
plt.plot(times, voltages, marker='o', markersize=3, linestyle='-')
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("ECG Waveform Over Time")
plt.grid(True)
plt.show()
