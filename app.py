from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import re

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="redundancy-db.chyykasawo01.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="Siddiqui",
    database="redundancy_db"
)

cursor = db.cursor(dictionary=True)

@app.route("/")
def home():
    return jsonify({
        "message": "Flask API is running successfully"
    })

@app.route("/api/submit", methods=["POST"])
def submit_record():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not email or not phone:
        return jsonify({
            "kind": "error",
            "title": "Missing Fields",
            "detail": "Name, email, and phone number are required."
        })

    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(email_pattern, email):
        return jsonify({
            "kind": "error",
            "title": "Invalid Email",
            "detail": "Email format is invalid."
        })

    cursor.execute(
        "SELECT * FROM records WHERE email=%s OR phone=%s",
        (email, phone)
    )

    existing = cursor.fetchone()

    if existing:
        return jsonify({
            "kind": "warning",
            "title": "Duplicate Entry",
            "detail": "Email or phone number already exists. Record was not stored."
        })

    cursor.execute(
        "INSERT INTO records(name, email, phone) VALUES(%s, %s, %s)",
        (name, email, phone)
    )

    db.commit()

    return jsonify({
        "kind": "success",
        "title": "Successfully Stored",
        "detail": "Unique data stored successfully in MySQL database."
    })

@app.route("/api/records", methods=["GET"])
def get_records():
    cursor.execute("SELECT * FROM records ORDER BY id DESC")
    records = cursor.fetchall()

    return jsonify(records)

if __name__ == "__main__":
    app.run(debug=True)