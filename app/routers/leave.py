from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix='/leaves', tags=['Leaves'])

@router.post('/', response_model=schemas.LeaveOut)
def create_leave(leave_details:schemas.Leave, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.id == leave_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee with id of: {leave_details.employee_id} does not exist.')
    new_leave = models.Leave(**leave_details.dict())
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave

@router.get('/', response_model=List[schemas.LeaveOut])
def get_leaves(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    leaves = db.query(models.Leave).all()
    return leaves

@router.get('/{leave_id}', response_model=schemas.LeaveOut)
def get_leave(leave_id: int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return leave

@router.put('/{leave_id}')
def update_leave(leave_id: int, leave_details:schemas.Leave, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.id == leave_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee with id of: {leave_details.employee_id} does not exist.')
    leave_query = db.query(models.Leave).filter(models.Leave.id == leave_id)
    leave = leave_query.first()
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    leave_query.update(leave_details.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Successfully updated"}

@router.delete('/{leave_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(leave_id: int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    leave_query = db.query(models.Leave).filter(models.Leave.id == leave_id)
    leave = leave_query.first()
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    leave_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)