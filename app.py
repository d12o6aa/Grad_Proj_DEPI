from flask import Flask, jsonify, render_template, request
import csv
from datetime import datetime
import os
import base64

app = Flask(__name__)
camera = None
camera_active = False
@app.route('/health')
def health():
    return "OK", 200
STATIC_IMAGES = {
    "Success": "/static/images/freepik__adjust__49088.png",
    "Failed": "/static/images/freepik__adjust__49086.png",
    "Fake": "/static/images/freepik__adjust__49087.png"
}

UPLOAD_FOLDER = "/home/doaa/Test/Grad_Proj_DEPI/Data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
                continue

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

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    global camera, camera_active
    if camera_active and camera is not None:
        camera.release()
        camera = None
        camera_active = False
        
    if request.method == 'POST':
        try:
            name = request.form['name']
            employee_folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
            os.makedirs(employee_folder, exist_ok=True)

            def save_base64_image(base64_str, filename):
                image_data = base64.b64decode(base64_str.split(',')[1])
                filepath = os.path.join(employee_folder, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)

            if request.form['image1']:
                save_base64_image(request.form['image1'], f"{name}_front.jpg")
            if request.form['image2']:
                save_base64_image(request.form['image2'], f"{name}_left.jpg")
            if request.form['image3']:
                save_base64_image(request.form['image3'], f"{name}_right.jpg")
        
            return f"✔️ تمت إضافة الموظف {name} بالصور بنجاح."
        except KeyError as e:
            return "Missing form field: " + str(e), 400

    return render_template('add_employee.html')

@app.route('/')
def index():
    return render_template("dashboard.html")

if __name__ == '__main__':
    app.run(debug=True)
