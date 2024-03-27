from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.errors import Error404, Error409
from .. import models, utils, schemas, database
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(
    user_details: schemas.UserCreate,
    user_role: schemas.Role,
    employee_details: schemas.EmployeeCreate,
    db: Session = Depends(database.get_db),
):
    department = (
        db.query(models.Department)
        .filter(models.Department.id == employee_details.department_id)
        .first()
    )
    if department is None:
        raise Error404("User's department does not exist")

    user = db.query(models.User).filter(models.User.email == user_details.email).first()
    if user is not None:
        raise Error409("User with the same email already exists")

    hashed_password = utils.hash(user_details.password)
    user_details.password = hashed_password
    new_user = models.User(**user_details.model_dump(), role=user_role.value)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    employee = (
        db.query(models.Employee).filter(models.Employee.user_id == new_user.id).first()
    )
    if employee is not None:
        raise Error409("Employee profile already exist")

    new_employee = models.Employee(**employee_details.model_dump(), user_id=new_user.id)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_user


@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} does not exist.",
        )
    return user
