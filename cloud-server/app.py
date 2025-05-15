from flask import Flask, jsonify, render_template
import csv
from datetime import datetime
import os

app = Flask(__name__)

# مسار الصور الثابتة في static
STATIC_IMAGES = {
    "Success": "/static/images/freepik__adjust__49088.png",
    "Failed": "/static/images/freepik__adjust__49086.png",
    "Fake": "/static/images/freepik__adjust__49087.png"
}

@app.route('/api/registrations')
def get_registrations():
    records = []

    with open("verification_results.csv", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
            status = "Failed"
            if "FAKE" in row['status']:
                status = "Fake"
            
            photo = STATIC_IMAGES.get(status, STATIC_IMAGES["Failed"])

            records.append({
                "name": row['name'],
                "date": ts.date().isoformat(),
                "time": ts.strftime("%H:%M:%S"),
                "status": status,
                "photo": photo
            })

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
