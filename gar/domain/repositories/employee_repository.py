# domain/repositories/employee_repo.py
from infrastructure.database.db import SessionLocal
from domain.entities.employee import Employee
import numpy as np
import pickle

class EmployeeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def save(self, name, vector):
        vector_binary = pickle.dumps(vector)  # convert numpy array to binary
        employee = Employee(name=name, vector=vector_binary)
        self.db.add(employee)
        self.db.commit()

    def get_all_vectors(self):
        employees = self.db.query(Employee).all()
        return [(emp.name, pickle.loads(emp.vector)) for emp in employees]
