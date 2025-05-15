from flask import Flask
from app.routes.employee_routes import employee_routes
from infrastructure.database.db import Base, engine
from domain.repositories.employee_repo import EmployeeRepository
from scipy.spatial.distance import cosine
from deepface import DeepFace


app = Flask(__name__)
app.register_blueprint(employee_routes)

Base.metadata.create_all(bind=engine)

def verify_identity_vector(img):
    repo = EmployeeRepository()
    try:
        embedding = DeepFace.represent(img_path=img, model_name="VGG-Face")[0]["embedding"]
        current_vector = np.array(embedding)

        for name, db_vector in repo.get_all_vectors():
            dist = cosine(current_vector, db_vector)
            if dist < 0.3:
                log_identity_if_new(name)
                return name
    except Exception as e:
        print("❌ Verification error:", e)
    return None


if __name__ == '__main__':
    app.run(debug=True)
