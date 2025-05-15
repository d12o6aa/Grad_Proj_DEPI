import cv2
import dlib
from scipy.spatial import distance
import numpy as np
import math

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def detect_blink(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)
        
        left_eye = landmarks.parts()[36:42]
        right_eye = landmarks.parts()[42:48]
        
        left_eye_points = [(p.x, p.y) for p in left_eye]
        right_eye_points = [(p.x, p.y) for p in right_eye]

        left_eye_distance = distance.euclidean(left_eye_points[1], left_eye_points[5]) 
        right_eye_distance = distance.euclidean(right_eye_points[1], right_eye_points[5])

        if left_eye_distance < 4 or right_eye_distance < 4:
            return False  # blink detected

    return True  # no blink (live)

def detect_head_movement(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)
        
        nose = (landmarks.part(30).x, landmarks.part(30).y)
        left_eye = (landmarks.part(36).x, landmarks.part(36).y)
        right_eye = (landmarks.part(45).x, landmarks.part(45).y)
        
        angle = calculate_head_rotation(left_eye, right_eye, nose)

        if abs(angle) < 5:
            return False  # no head movement

    return True  # head moved

def calculate_head_rotation(left_eye, right_eye, nose):
    delta_x = right_eye[0] - left_eye[0]
    delta_y = right_eye[1] - left_eye[1]
    angle = math.atan2(delta_y, delta_x) * 180 / math.pi
    return angle
