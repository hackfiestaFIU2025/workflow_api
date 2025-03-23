import serial
import time
import subprocess
import io
import os
from BeatAI import filter
import firebase_admin
from firebase_admin import credentials, storage, db
import matplotlib.pyplot as plt
from heart_live_model import outside_file_predict
import pandas as pd
import numpy
import joblib

# Initialize Firebase (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://beatai-bc460-default-rtdb.firebaseio.com/',
        'storageBucket': "beatai-bc460.firebasestorage.app"   #"beatai-bc460.appspot.com" # Replace with your bucket name "beatai-bc460.firebasestorage.app"
    })

userRef = db.reference("heart_risk/session")


while True:
    userBool = userRef.child("UP").get()
    if userBool == 0:   #should be 0
        print("⚠️ User has not started the task yet.")
        time.sleep(3)
    else:
        print("✅ User has started the task.")
        # Specify the correct serial port (COMx for Windows or /dev/ttyUSBx for Linux/Mac)
        arduino = serial.Serial('COM6', 115200)  # Adjust COM port and baud rate

        # Send a command to the Arduino
        command = "run"  # You can replace this with any command
        # arduino.write((command + '\n').encode())  # Send the command with newline to simulate pressing Enter
        # Wait for the response from the Arduino
        response = ""

        while response.find("Command received: Starting process...") == -1:
            arduino.write((command + '\n').encode())  # Send the command with newline to simulate pressing Enter
            response = arduino.readline().decode().strip()  # Read and decode the response
            time.sleep(2)


        while response.find("Data sent to the server") == -1:
            response = arduino.readline().decode().strip()  # Read and decode the response

        # Close the serial connection
        arduino.close()

        time.sleep(3)

        # Wait for 11 seconds before running the next task (to finish uploading code)

        ref = db.reference("heart_risk/session")
        raw_data = ref.child("raw_data").get()
        client_data = ref.child("user_input").get()
            
        if not raw_data or len(raw_data) == 0:
            print("⚠️ No raw ECG data found in 'raw_data'.")


        bpm = filter.calculate_bpm(raw_data, sample_rate=40, refractory_period=10)

        # # Define Age and Cholesterol values
        # age = client_data.get('Age') # Example age value
        # cholesterol = client_data.get('Cholesterol')  # Example cholesterol value

        # # Initialize the result to 0
        # result = 0

        # # Use a for loop to add 'age' to itself 'cholesterol' times
        # for _ in range(cholesterol):
        #     result += age

        Heart_Rate = bpm
        clientArr = [
            client_data.get('Age'),
            client_data.get('Sex'),
            client_data.get('Cholesterol'),
            client_data.get('Triglycerides'),
            client_data.get('Systolic'),
            client_data.get('Diastolic'),
            client_data.get('BMI'),
            client_data.get('Smoking'),
            client_data.get('Diabetes'),
            client_data.get('Exercise_Hours_Per_Week'),
            Heart_Rate
            # result
        ]
        print(type)
        # clientArr.append(client_data.get('Age') * client_data.get('Cholesterol'))

        attackBool = outside_file_predict(clientArr, 'C:/Users/natha/Documents/GitHub/python_projects/BeatAI/logistic_pipeline_with_heart_rate.pkl') 
        
        ref.child("Prediction").update({"risk": attackBool})
        if attackBool == 1:
            print("⚠️ Heart Attack detected!")
        else:
            print("✅ No Heart Attack detected")
        # order it like this
        #  columns = ['Age', 'Sex', 'Cholesterol', 'Triglycerides', 'Systolic', 'Diastolic',
        #   'BMI', 'Smoking', 'Diabetes', 'Exercise_Hours_Per_Week', 'Age_Cholesterol']

        # Write the calculated BPM to Firebase under heart_rate (no timestamp needed)
        ref.child("heart_rate").update({"BPM": bpm})
        print(f"✅ BPM calculated and stored: {bpm} BPM")

        userRef.update({"UP": 0})
        print("✅ Updated UP to 0")

        # #Extract time and voltage values into separate lists
        # times = [entry["time"] for entry in raw_data]
        # #Plot the waveform
        # voltages = [entry["voltage"] for entry in raw_data]
        # plt.figure(figsize=(12, 6))
        # plt.plot(times, voltages, marker='o', markersize=3, linestyle='-')
        # plt.xlabel("Time (ms)")
        # plt.ylabel("Voltage (V)")
        # plt.title("ECG Waveform Over Time")
        # plt.grid(True)

        # # Save the plot to a BytesIO object (in-memory)
        # img_byte_arr = io.BytesIO()
        # plt.savefig(img_byte_arr, format='png')
        # img_byte_arr.seek(0)  # Go to the start of the BytesIO object
        # print(f"✅ Saved plot as {img_byte_arr}.{"png"}")
        # # Save the plot as a PNG image
        # # Save the plot to a BytesIO object
        # image_stream = io.BytesIO()
        # plt.savefig(image_stream, format='png')
        # image_stream.seek(0)  # Go back to the start of the BytesIO stream

        # bucket = storage.bucket("beatai-bc460.firebasestorage.app")
        # blob = bucket.blob('graph/plot.png')

        # # Upload the image from the BytesIO object
        # blob.upload_from_file(image_stream, content_type='image/png')

        # # Get the URL of the uploaded image
        # image_url = blob.public_url

        # # Optionally, save the URL in Firebase Realtime Database
        # ref = db.reference('heart_risk/session/graph')
        # ref.push({
        #     'title': 'Plot',
        #     'url': image_url
        # })
                
        # # Ensure the image file exists at the specified path
        # image_path = "heart_risk/session/"
        # if os.path.exists(image_path):
        #     blob.upload_from_filename(image_path)
        #     print(f'File {image_path} uploaded to images/my_image.jpg.')
        # else:
        #     print(f"Error: Image file not found at {image_path}")
    
        # # To make the file public
        # blob.make_public()
        # print(blob.public_url)
