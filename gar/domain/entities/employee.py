# domain/entities/employee.py
from sqlalchemy import Column, Integer, String, LargeBinary
from infrastructure.database.db import Base

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector = Column(LargeBinary, nullable=False)  # we'll store vector as binary
