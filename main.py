from fastapi import FastAPI
from app import models, schemas, database
from app.database import engine
from app.routers import (
    user,
    auth,
    department,
    employee,
    grade,
    employee_grade,
    leave,
    clocking,
    leave_type,
    leave_days_left,
    sell_leave,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status, HTTPException, Depends
from sqlalchemy.orm import Session
import uvicorn

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/home")
def index() -> dict:
    return {"message": "This is the home page"}


@app.post("/create_department", status_code=status.HTTP_201_CREATED)
def create_department(db: Session = Depends(database.get_db)):
    new_department = models.Department(department="Human Resources")
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return {"message": "Department successfully added"}


@app.post("/create_grade", status_code=status.HTTP_201_CREATED)
def create_grade(db: Session = Depends(database.get_db)):
    new_grade = models.Grade(grade="1 to 12", leave_days=24)
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return {"message": "Grade successfully added"}


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(department.router)
app.include_router(employee.router)
app.include_router(grade.router)
app.include_router(leave_type.router)
app.include_router(leave.router)
app.include_router(leave_days_left.router)
app.include_router(employee_grade.router)
app.include_router(sell_leave.router)
app.include_router(clocking.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
