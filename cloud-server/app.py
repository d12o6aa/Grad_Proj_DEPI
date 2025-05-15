from flask import Flask, jsonify, render_template
import csv
from datetime import datetime
import os

app = Flask(__name__)

STATIC_IMAGES = {
    "Success": "/static/images/freepik__adjust__49088.png",
    "Failed": "/static/images/freepik__adjust__49086.png",
    "Fake": "/static/images/freepik__adjust__49087.png"
}

@app.route('/api/registrations')
def get_verification_results():
    records = []

    with open("verification_results.csv", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")

            if "FAKE" in row['status']:
                status = "Fake"
                photo = STATIC_IMAGES.get("Fake", STATIC_IMAGES["Failed"])
            elif "Registration Failed" in row['status']:
                status = "Failed"
                photo = STATIC_IMAGES.get("Failed")
            elif "Verified" in row['status']:
                status = "Success"
                photo = STATIC_IMAGES.get("Success")
            else:
                continue  # ignore unknown statuses

            records.append({
                "name": row['name'],
                "date": ts.date().isoformat(),
                "time": ts.strftime("%H:%M:%S"),
                "status": status,
                "photo": photo
            })

    records.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)

    return jsonify(records)

@app.route('/api/verified-log')
def get_verified_log():
    records = []

    with open("verified_log.csv", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            photo = STATIC_IMAGES["Success"]

            records.append({
                "name": row['name'],
                "date": row['date'],
                "time": row['time'],
                "status": "Success",
                "photo": photo
            })

    records.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)

    return jsonify(records)


@app.route('/')
def index():
    return render_template("dashboard.html")

if __name__ == '__main__':
    app.run(debug=True)
