import face_recognition
import base64
import numpy as np
import cv2

def has_face(image_base64):
    img_data = base64.b64decode(image_base64.split(',')[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    face_locations = face_recognition.face_locations(img)
    return len(face_locations) > 0
