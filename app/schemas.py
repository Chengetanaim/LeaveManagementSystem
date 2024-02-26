from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Role(str, Enum):
    admin = "Admin"
    regular_user = "Regular User"


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

class EmployeeCreate(Employee):
    pass

class EmployeeOut(Employee):
    id:int
    department: Department
    user_id: int
    user: UserOut

class Grade(BaseModel):
    grade: str
    leave_days: int

class GradeOut(Grade):
    id: int

class EmployeeGrade(BaseModel):
    grade_id: int
    employee_id: int

class Leave(BaseModel):
    start_date: datetime
    end_date: datetime
    employee_id:int
    leave_type: str

class LeaveOut(Leave):
    id: int
    employee: EmployeeOut

class Clocking(BaseModel):
    clock_in: datetime
    clock_out: datetime
    employee_id: int

    class Config:
        orm_mode = True

class ClockingOut(BaseModel):
    id: int
    employee: Employee
