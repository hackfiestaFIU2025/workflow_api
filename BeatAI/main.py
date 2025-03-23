import firebase_admin
from firebase_admin import credentials, db

# Load your Firebase service account key
cred = credentials.Certificate("firebase-key.json")

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://beatai-bc460-default-rtdb.firebaseio.com/'
})

# Reference session1
ref = db.reference("heart_risk/session/")

# Fake user inputs
user_inputs = {
    "Age": 55,
    "Sex": "Male",
    "Cholesterol": 240,
    "Systolic": 130,
    "Diastolic": 85,
    "BP_Ratio": 1.53,
    "Diabetes": 1,
    "Family History": 1,
    "Smoking": 1,
    "Obesity": 0,
    "Alcohol Consumption": 2,
    "Exercise Hours Per Week": 1.5,
    "Diet": "Poor",
    "Previous Heart Problems": 1,
    "Medication Use": 1,
    "Stress Level": 3,
    "Sedentary Hours Per Day": 9.0,
    "Income": 45000,
    "BMI": 27.5,
    "Triglycerides": 180,
    "Physical Activity Days Per Week": 2,
    "Sleep Hours Per Day": 6
}

ref.child("user_input").update(user_inputs)   # Only updates the provided keys


print("✅ Fake heart risk data successfully written to Firebase!")