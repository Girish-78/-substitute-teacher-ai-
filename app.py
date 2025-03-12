from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
import os

app = Flask(__name__)

# Securely get JSON file from Render or Colab
json_key_path = "/etc/secrets/service-account.json"  # Use this for Render
# json_key_path = "/content/newsubst_colab_key.json"  # Use this if testing in Colab

# Define the required scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Authenticate using the service account key
creds = Credentials.from_service_account_file(json_key_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Open Google Sheets
substitutes_sheet = client.open("Substitutes").sheet1
teachers_sheet = client.open("Available Teachers").sheet1

# Function to get substitute teacher
def find_substitute(absent_teacher, period):
    absent_data = substitutes_sheet.get_all_records()
    available_data = teachers_sheet.get_all_records()

    subject = next((item['Subject'] for item in absent_data if item['Teacher Name'] == absent_teacher), None)
    if not subject:
        return f"Teacher {absent_teacher} not found in Substitutes list."

    available_teachers = [t['Teacher Name'] for t in available_data if t['Subject'] == subject and str(period) in str(t['Free Periods'])]

    if available_teachers:
        return f"Assign {available_teachers[0]} for period {period}"
    else:
        return "No available substitute found."

# Flask API routes
@app.route("/")
def home():
    return "Flask is running!"

@app.route("/get_substitute", methods=["POST"])
def get_substitute():
    data = request.json
    teacher = data.get("teacher")
    period = data.get("period")
    result = find_substitute(teacher, period)
    return jsonify({"Substitute": result})

if __name__ == "__main__":
    app.run(debug=True)

