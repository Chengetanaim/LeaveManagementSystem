from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
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
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no department of id: {employee_details.department_id}",
        )
    user = db.query(models.User).filter(models.User.email == user_details.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with this email already exist.",
        )
    hashed_password = utils.hash(user_details.password)
    user_details.password = hashed_password
    new_user = models.User(**user_details.dict(), role=user_role.value)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    employee = (
        db.query(models.Employee).filter(models.Employee.user_id == new_user.id).first()
    )
    if employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have an employee profile",
        )

    new_employee = models.Employee(**employee_details.dict(), user_id=new_user.id)
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
