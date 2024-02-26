from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    department = relationship("Department")
    gender = Column(String, nullable=False)
    position = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
   
class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, nullable=False)
    grade = Column(String, nullable=False)
    leave_days = Column(Integer, nullable=False)

class EmployeeGrade(Base):
    __tablename__ = "employee-grades"
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, primary_key=True)

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True, nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    employee = relationship("Employee")
    leave_type = Column(String, nullable=False)

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, nullable=False)
    department = Column(String, nullable=False)

class Clocking(Base):
    __tablename__ = "clockings"
    id = Column(Integer, primary_key=True, nullable=False)
    clock_in = Column(TIMESTAMP(timezone=True), nullable=False)
    clock_out = Column(TIMESTAMP(timezone=True), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    employee = relationship("Employee")