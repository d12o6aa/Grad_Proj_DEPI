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
import base64
from datetime import datetime
import numpy as np

app = Flask(__name__)

executor = ThreadPoolExecutor()

frame = None
spoof_results = []
frame_count = 0
THRESHOLD = 20
final_spoof_result = None
identity_verified = False
checked_identity = False
camera = None
streaming_thread = None
camera_active = False

LOG_FILE = "verified_log.csv"
RESULTS_LOG_FILE = "verification_results.csv"
UPLOAD_FOLDER = "/home/doaa/Test/Grad_Proj_DEPI/Data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
IDEAL_FACE_AREA = 30000
TOLERANCE_RATIO = 0.5
current_name = "Unknown"
UPLOAD_FOLDER_DATA = "/home/doaa/Test/Grad_Proj_DEPI/static"
app.config['UPLOAD_FOLDER_DATA'] = UPLOAD_FOLDER_DATA
FAKE_FOLDER = os.path.join(app.config['UPLOAD_FOLDER_DATA'], 'fake_frames')
VERIFIED_FOLDER = os.path.join(app.config['UPLOAD_FOLDER_DATA'], 'verified_frames')
FAILED_FOLDER = os.path.join(app.config['UPLOAD_FOLDER_DATA'], 'failed_frames')
os.makedirs(FAILED_FOLDER, exist_ok=True)
os.makedirs(FAKE_FOLDER, exist_ok=True)
os.makedirs(VERIFIED_FOLDER, exist_ok=True)
pending_verified_frame = None


# ======================= Logging Functions =======================

def save_detailed_result_to_log(status, name="Unknown", identity_status="Not Checked"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(RESULTS_LOG_FILE):
        with open(RESULTS_LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["status", "timestamp", "name", "identity_status"])
    with open(RESULTS_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([status, timestamp, name, identity_status])

def save_frame_image(img, folder, prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prefix}_{timestamp}.jpg"
    filepath = os.path.join(folder, filename)
    cv2.imwrite(filepath, img)
    return filepath

def save_frame_image_with_status(img, status):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], "frames")
    os.makedirs(folder, exist_ok=True)
    prefix = "verified" if status else "not_verified"
    return save_frame_image(img, folder, prefix)

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

# ======================= Identity Verification =======================

def verify_identity(img):
    global identity_verified, checked_identity, current_name
    identity_verified = False
    checked_identity = False
    print("[DEBUG] Starting identity verification...")
    print(f"[DEBUG] Image path received: {img}")
    
    try:
        result = DeepFace.find(
            img_path=img,
            db_path=app.config['UPLOAD_FOLDER'],
            model_name="Facenet512",
            enforce_detection=False
        )
        
        print("[DEBUG] DeepFace.find() completed.")
        print(f"[DEBUG] Result type: {type(result)}, Length: {len(result)}")
        
        if isinstance(result, list) and len(result) > 0 and not result[0].empty:
            print("[DEBUG] Full match result:")
            print(result[0].head())

            top_match = result[0].iloc[0]
            print("[DEBUG] Top match keys:", top_match.keys())

            cosine_score = top_match.get('distance', None)
            print("[DEBUG] Cosine score (distance):", cosine_score)

            if cosine_score is not None and cosine_score < 0.4:
                identity_verified = True
                match_path = top_match["identity"]
                print(f"[DEBUG] Match found at path: {match_path}")
                
                current_name = os.path.basename(os.path.dirname(match_path))
                print(f"[DEBUG] Extracted name from path: {current_name}")
                
                log_identity_if_new(current_name)
            else:
                print("[DEBUG] Match found but distance too high:", cosine_score)
                current_name = "Unknown"
                identity_verified = False
        else:
            print("[DEBUG] No faces matched in the database.")
            identity_verified = False
            current_name = "Unknown"

    except Exception as e:
        print("[ERROR] Exception in DeepFace verification:", str(e))
        identity_verified = False
        current_name = "Unknown"

    checked_identity = True
    print(f"[DEBUG] identity_verified: {identity_verified}, checked_identity: {checked_identity}")

    if identity_verified:
        print("✅ Verification successful.")
        if pending_verified_frame is not None:
            save_frame_image(pending_verified_frame, VERIFIED_FOLDER, f"verified_{current_name}")
        else:
            print("[WARNING] No frame available to save despite successful verification.")
    else:
        print("❌ Verification failed.")

# ======================= Helper =======================

def is_face_area_within_range(face_area):
    min_area = IDEAL_FACE_AREA * 0.01
    max_area = IDEAL_FACE_AREA * 100
    return min_area <= face_area <= max_area

def reset_verification():
    global final_spoof_result, identity_verified, checked_identity, current_name
    global pending_verified_frame, spoof_results, frame_count
    final_spoof_result = None
    identity_verified = False
    checked_identity = False
    current_name = "Unknown"
    spoof_results = []
    frame_count = 0
    pending_verified_frame = None

# ======================= Frame Handling =======================

def update_frame():
    global frame, spoof_results, frame_count, final_spoof_result
    global identity_verified, checked_identity, camera, camera_active

    while camera_active and camera is not None:
        success, img = camera.read()
        if not success:
            continue

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        try:
            if detect_blink(img) and detect_head_movement(img):
                detected_faces = DeepFace.extract_faces(
                    img_path=img,
                    detector_backend="opencv",
                    enforce_detection=False,
                    align=False,
                    anti_spoofing=True
                )
                valid_faces = [f for f in detected_faces if f.get("confidence", 0) >= 0.80]

                if len(valid_faces) != 1:
                    reset_verification()
                    time.sleep(0.1)
                    continue

                face = valid_faces[0]
                is_real = face.get("is_real", None)
                if is_real is None:
                    continue

                spoof_results.append(is_real)
                frame_count += 1

                if frame_count >= THRESHOLD:
                    real_count = spoof_results.count(True)
                    fake_count = spoof_results.count(False)
                    real_ratio = real_count / THRESHOLD
                    final_spoof_result = real_ratio >= 0.8
                    spoof_results = []
                    frame_count = 0
                    print(f"🎯 Total Frames Checked: {THRESHOLD}")
                    print(f"✅ Real Frames: {real_count}")
                    print(f"❌ Fake Frames: {fake_count}")
                    print(f"🔍 Final Spoof Result: {final_spoof_result}")

                    if final_spoof_result and not checked_identity:
                        face_area = face.get("facial_area", {}).get("w", 0) * face.get("facial_area", {}).get("h", 0)
                        if is_face_area_within_range(face_area):
                            pending_verified_frame = img.copy()
                            executor.submit(verify_identity, pending_verified_frame)
                        else:
                            print("🚫 Face not at optimal distance for verification.")
                    else:
                        save_frame_image(img.copy(), FAKE_FOLDER, "fake")
                        save_detailed_result_to_log("FAKE (frame)")
                        reset_verification()

        except Exception as e:
            print("Error in liveness detection:", e)
        time.sleep(0.1)

# ======================= Flask Routes =======================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global camera, camera_active, streaming_thread
    if not camera_active or camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return "Camera failed to open", 500
        camera_active = True
        streaming_thread = threading.Thread(target=update_frame, daemon=True)
        streaming_thread.start()

    def generate():
        global frame
        while camera_active:
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    global camera, camera_active
    if camera_active and camera is not None:
        camera.release()
        camera = None
        camera_active = False
    return "Camera stopped"

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

@app.route('/result')
def result():
    global final_spoof_result, identity_verified, checked_identity, current_name, frame

    if final_spoof_result is None:
        return jsonify({"status": "Analyzing..."})

    if not final_spoof_result:
        save_detailed_result_to_log("❌ FAKE", name="Unknown", identity_status="Not Checked")
        reset_verification()
        return jsonify({"status": "❌ FAKE"})

    if final_spoof_result and not checked_identity:
        return jsonify({"status": "Verifying identity..."})

    if identity_verified:
        save_detailed_result_to_log("✅ Verified", name=current_name, identity_status="Matched")
        threading.Timer(5.0, reset_verification).start()
        final_spoof_result = None
        return jsonify({"status": "✅ Verified"})

    if current_name == "Unknown" and checked_identity:
        return jsonify({"status": "❌ Registration Failed"})

    save_detailed_result_to_log("❌ Registration Failed", name="Unknown", identity_status="Not Matched")

    if frame is not None:
        nparr = np.frombuffer(frame, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        filename = f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_frame_image(img_np, FAILED_FOLDER, filename)

    reset_verification()
    return jsonify({"status": "❌ Registration Failed"})

# ======================= Start Server =======================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
