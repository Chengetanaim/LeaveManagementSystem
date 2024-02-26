from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix='/clockings', tags=['Clockings'])

@router.post('/', response_model=schemas.ClockingOut, status_code=status.HTTP_201_CREATED)
def create_clocking(clocking_details:schemas.Clocking, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.id == clocking_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee with id of: {clocking_details.employee_id} does not exist.')
    new_clocking = models.Clocking(**clocking_details.dict())
    db.add(new_clocking)
    db.commit()
    db.refresh(new_clocking)
    return new_clocking

@router.get('/', response_model=List[schemas.ClockingOut])
def get_clockings(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    clockings = db.query(models.Clocking).all()
    return clockings

@router.get('/{clocking_id}', response_model=schemas.ClockingOut)
def get_clocking(clocking_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    clocking = db.query(models.Clocking).filter(models.Clocking.id == clocking_id).first()
    if not clocking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return clocking

@router.put('/{clocking_id}')
def update_clocking(clocking_id:int, clocking_details:schemas.Clocking, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.id == clocking_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee with id of: {clocking_details.employee_id} does not exist.')
    clocking_query = db.query(models.Clocking).filter(models.Clocking.id == clocking_id)
    clocking = clocking_query.first()
    if not clocking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    clocking_query.update(clocking_details.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Updated successfully"}

@router.delete('/{clocking_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_clocking(clocking_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    clocking_query = db.query(models.Clocking).filter(models.Clocking.id == clocking_id)
    clocking = clocking_query.first()
    if not clocking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    clocking_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

