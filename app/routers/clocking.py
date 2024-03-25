from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.errors import Error404
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix="/clockings", tags=["Clockings"])


@router.post(
    "/", response_model=schemas.ClockingOut, status_code=status.HTTP_201_CREATED
)
def create_clocking(
    clocking_details: schemas.Clocking,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    employee = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User does not have an employee profile",
        )

    new_clocking = models.Clocking(
        **clocking_details.model_dump(), employee_id=employee.id
    )
    db.add(new_clocking)
    db.commit()
    db.refresh(new_clocking)
    return new_clocking


@router.get("/", response_model=List[schemas.ClockingOut])
def get_clockings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    employee = db.query(models.Employee).filter_by(user_id=current_user.id).first()
    if employee is None:
        raise Error404(message="Employee not found.")

    clockings = db.query(models.Clocking).filter_by(employee_id=employee.id).all()
    return clockings


@router.get("/{clocking_id}", response_model=schemas.ClockingOut)
def get_clocking(
    clocking_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    clocking = (
        db.query(models.Clocking).filter(models.Clocking.id == clocking_id).first()
    )
    if not clocking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )
    return clocking


@router.put("/{clocking_id}")
def update_clocking(
    clocking_id: int,
    clocking_details: schemas.Clocking,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    employee = db.query(models.Employee).filter_by(user_id=current_user.id).first()
    if employee is None:
        raise Error404("Employee is not found.")

    clocking_query = db.query(models.Clocking).filter(models.Clocking.id == clocking_id)
    clocking = clocking_query.first()
    if clocking is None:
        raise Error404("Clocking is not found.")

    clocking_query.update(**clocking_details.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Updated successfully"}


@router.delete("/{clocking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clocking(
    clocking_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    clocking_query = db.query(models.Clocking).filter(models.Clocking.id == clocking_id)
    clocking = clocking_query.first()
    if not clocking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )
    clocking_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
