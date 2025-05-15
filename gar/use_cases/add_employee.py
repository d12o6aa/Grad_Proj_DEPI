# use_cases/add_employee.py
from deepface import DeepFace
import cv2
import numpy as np
from domain.repositories.employee_repo import EmployeeRepository

def extract_and_store_vectors(name, image_paths):
    repo = EmployeeRepository()
    for img_path in image_paths:
        embedding = DeepFace.represent(img_path=img_path, model_name="VGG-Face")[0]["embedding"]
        vector = np.array(embedding)
        repo.save(name, vector)
