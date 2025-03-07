from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is running!"

@app.route("/get_substitute", methods=["POST"])
def get_substitute():
    data = request.json
    teacher = data.get("teacher")
    period = data.get("period")
    return jsonify({"message": f"Finding substitute for {teacher} in period {period}"})

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

app = Flask(__name__)

# Path to your JSON key file
json_key_path = "subst_colab_key.json"

# Define the required scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Authenticate using the service account key
creds = Credentials.from_service_account_file(json_key_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Open Google Sheets
absent_teachers = client.open("Substitutes").sheet1
available_teachers = client.open("Available Teachers").sheet1

# Function to get data from sheets
def get_data():
    absent_data = pd.DataFrame(absent_teachers.get_all_records())
    available_data = pd.DataFrame(available_teachers.get_all_records())
    return absent_data, available_data

# AI Logic: Find best substitute teacher
def find_substitute(absent_teacher, period):
    absent_data, available_data = get_data()
    subject = absent_data.loc[absent_data['Teacher Name'] == absent_teacher, 'Subject'].values[0]

    available_teachers_list = available_data[
        (available_data['Subject'] == subject) & 
        (available_data['Free Periods'].apply(lambda x: str(period) in str(x)))
    ]

    if not available_teachers_list.empty:
        substitute = available_teachers_list.iloc[0]['Teacher Name']
        return f"Assign {substitute} for period {period}"
    else:
        return "No available substitute found."

# API Endpoint
@app.route("/get_substitute", methods=["POST"])
def get_substitute():
    data = request.json
    teacher = data["teacher"]
    period = data["period"]
    result = find_substitute(teacher, period)
    return jsonify({"Substitute": result})

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
