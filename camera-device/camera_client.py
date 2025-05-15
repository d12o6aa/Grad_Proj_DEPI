# camera_client.py

import cv2
import face_recognition
import requests
import datetime
import base64

SERVER_URL = "https://your-cloud-api.com/attendance"  # غيّريها لـ URL الحقيقي

def capture_face_and_send():
    video = cv2.VideoCapture(0)
    print("🔴 تشغيل الكاميرا...")

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            print("✅ تم التقاط وجه")
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            payload = {
                "name": "Employee1",  # المفروض تحددي الاسم بناءً على الـ encoding
                "photo": img_base64,
                "time": timestamp,
                "status": "Success"
            }

            try:
                response = requests.post(SERVER_URL, json=payload)
                print("✅ تم إرسال البيانات: ", response.status_code)
            except Exception as e:
                print("❌ فشل الإرسال:", e)

            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_face_and_send()
