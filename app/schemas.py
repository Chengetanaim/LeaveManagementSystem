from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Role(str, Enum):
    admin = "Admin"
    regular_user = "Regular User"


class Status(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"


class Department(BaseModel):
    department: str


class DepartmentOut(Department):
    id: int


class User(BaseModel):
    email: EmailStr


class UserCreate(User):
    password: str


class UserOut(User):
    id: int
    role: Role


class Employee(BaseModel):
    first_name: str
    last_name: str
    department_id: int
    gender: str
    position: str
    grade_id: int


class EmployeeCreate(Employee):
    pass


class Grade(BaseModel):
    grade: str
    leave_days: int


class GradeOut(Grade):
    id: int


class EmployeeGrade(BaseModel):
    grade_id: int
    # employee_id: int
    days_left: int


class Leave(BaseModel):
    start_date: datetime
    end_date: datetime
    leave_type_id: int


class LeaveType(BaseModel):
    leave_type: str
    leave_days: int


class LeaveOut(Leave):
    id: int
    employee_id: int
    status: str
    leave_type: LeaveType


class Clocking(BaseModel):
    clock_in: datetime
    clock_out: datetime

    class Config:
        from_attributes = True


class ClockingOut(Clocking):
    id: int
    employee: Employee


class LeaveTypeOut(LeaveType):
    id: int


class LeaveDaysLeft(BaseModel):
    type: str
    days: int
    days_used: int


class SellLeave(BaseModel):
    employee_id: int
    number_of_days: int
    leave_type_id: int


class EmployeeOut(Employee):
    id: int
    department: Department
    user_id: int
    user: UserOut
    leaves: list[LeaveOut] | None
    clockings: list[ClockingOut] | None
