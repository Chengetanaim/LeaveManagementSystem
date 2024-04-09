from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey  # type: ignore
from .database import Base
from sqlalchemy.orm import relationship  # type: ignore


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department_id = Column(
        Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    department = relationship("Department")
    gender = Column(String, nullable=False)
    position = Column(String, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User")
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"))
    grade = relationship("Grade")

    leaves = relationship("Leave", back_populates="employee")
    clockings = relationship("Clocking", back_populates="employee")


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
    grade_id = Column(
        Integer,
        ForeignKey("grades.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    days_left = Column(Integer)


# Leave Type decides how much days of leave to get
# Annual Leave has it's specific number of days per year, and so does sick leave and maternity leave
class LeaveType(Base):
    __tablename__ = "leave-types"
    id = Column(Integer, primary_key=True, nullable=False)
    leave_type = Column(String, nullable=False)
    leave_days = Column(Integer, nullable=False)


class LeaveDaysLeft(Base):
    __tablename__ = "leave-days-left"
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    employee = relationship("Employee")
    leave_type_id = Column(
        Integer,
        ForeignKey("leave-types.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    leave_type = relationship("LeaveType")
    days_left = Column(Integer, nullable=False)


class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True, nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    employee_id = Column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    employee = relationship("Employee", back_populates="leaves")
    leave_type_id = Column(Integer, ForeignKey("leave-types.id", ondelete="CASCADE"))
    leave_type = relationship("LeaveType")
    status = Column(String)

    def __repr__(self):
        return f"Leave<ID={self.id}, EmployeeID={self.employee_id}>"


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, nullable=False)
    department = Column(String, nullable=False)


class Clocking(Base):
    __tablename__ = "clockings"
    id = Column(Integer, primary_key=True, nullable=False)
    clock_in = Column(TIMESTAMP(timezone=True), nullable=False)
    clock_out = Column(TIMESTAMP(timezone=True), nullable=False)
    employee_id = Column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    employee = relationship("Employee")
