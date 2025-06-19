from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Konfiguration
SPREADSHEET_ID = "1pv6E2esRPSvYg5EU0GXvPVE1y25IW4U44s7tPJs56GQ"
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authentifiziere mit Google
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheet = build("sheets", "v4", credentials=creds).spreadsheets().values()

@app.route("/log_conversation", methods=["POST"])
def log_conversation():
    data = request.get_json()
    summary = data.get("summary", "")
    topic = data.get("topic", "Kein Thema")
    tab_name = data.get("sheet")  # <-- NEU: Welches Blatt?

    if not summary or not tab_name:
        return jsonify({"error": "Feld 'summary' und 'sheet' sind erforderlich."}), 400

    # Ziel-Range mit Tabellenblattnamen, z.B. "Instagram!A1"
    target_range = f"{tab_name}!A1"

    values = [[topic, summary]]
    body = {"values": values}

    try:
        sheet.append(
            spreadsheetId=SPREADSHEET_ID,
            range=target_range,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return jsonify({"status": "OK", "message": f"In Blatt '{tab_name}' gespeichert."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
