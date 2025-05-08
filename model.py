import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from liveness_detection import detect_blink, detect_head_movement

import cv2
from deepface import DeepFace
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, Response, jsonify, request
import csv
from datetime import datetime

app = Flask(__name__)
executor = ThreadPoolExecutor()

camera = cv2.VideoCapture(0)
frame = None
spoof_results = []
frame_count = 0
THRESHOLD = 20
final_spoof_result = None
identity_verified = False
checked_identity = False

LOG_FILE = "verified_log.csv"
UPLOAD_FOLDER = "/home/doaa/Test/Data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def log_identity_if_new(name):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["name", "date", "time"])

    with open(LOG_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["name"] == name and row["date"] == today:
                return

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, today, current_time])


def verify_identity(img):
    global identity_verified, checked_identity
    try:
        result = DeepFace.find(
            img_path=img,
            db_path=app.config['UPLOAD_FOLDER'],
            enforce_detection=False
        )
        if len(result[0]) > 0:
            identity_verified = True
            match_path = result[0].iloc[0]["identity"]
            name = os.path.basename(os.path.dirname(match_path))
            log_identity_if_new(name)
        else:
            identity_verified = False
    except Exception as e:
        print("Error in DeepFace verification:", e)
        identity_verified = False
    checked_identity = True


def update_frame():
    global frame, spoof_results, frame_count, final_spoof_result, identity_verified, checked_identity

    while True:
        success, img = camera.read()
        if not success:
            print("Failed to capture image")
            continue
        else:
            print("Image captured successfully")

        try:
            # Detect blink and head movement
            is_blinking = detect_blink(img)
            is_moving_head = detect_head_movement(img)

            if is_blinking and is_moving_head:
                faces = DeepFace.extract_faces(
                    img_path=img,
                    detector_backend="opencv",  # Try opencv instead of retinaface
                    enforce_detection=False,
                    anti_spoofing=True
                )

                if faces:
                    face = faces[0]
                    is_real = face["is_real"]
                    spoof_results.append(is_real)
                    frame_count += 1

                    if frame_count >= THRESHOLD:
                        real_count = spoof_results.count(True)
                        fake_count = spoof_results.count(False)
                        real_ratio = real_count / THRESHOLD

                        final_spoof_result = True if real_ratio >= 0.8 else False

                        spoof_results = []
                        frame_count = 0

                        if final_spoof_result and not checked_identity:
                            executor.submit(verify_identity, img.copy())

        except Exception as e:
            print("Error:", e)

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        time.sleep(0.1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        files = request.files.getlist('images')
        employee_folder = os.path.join(app.config['UPLOAD_FOLDER'], name)

        os.makedirs(employee_folder, exist_ok=True)

        for file in files:
            if file.filename:
                filepath = os.path.join(employee_folder, file.filename)
                file.save(filepath)

        return f"✔️ تمت إضافة الموظف {name} بنجاح."

    return render_template('add_employee.html')


@app.route('/result')
def result():
    if final_spoof_result is None:
        return jsonify({"status": "Analyzing..."})
    if not final_spoof_result:
        return jsonify({"status": "❌ FAKE"})
    if final_spoof_result and identity_verified is None:
        return jsonify({"status": "Verifying identity..."})
    if identity_verified:
        return jsonify({"status": "✅ Verified"})
    else:
        return jsonify({"status": "❌ Registration Failed"})


if __name__ == '__main__':
    threading.Thread(target=update_frame, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
