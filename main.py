from fastapi import FastAPI
from app import models
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
