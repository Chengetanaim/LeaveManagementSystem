from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List
from fastapi import Response

router = APIRouter(prefix='/departments', tags=['Departments'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.DepartmentOut)
def create_department(department_details:schemas.Department, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    new_department = models.Department(**department_details.dict())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department


@router.get('/', response_model=List[schemas.DepartmentOut])
def get_departments(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    departments = db.query(models.Department).all()
    return departments


@router.get('/{department_id}', response_model=schemas.DepartmentOut)
def get_department(department_id: int,db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id: {department_id} does not exist")
    return department

@router.put('/{department_id}')
def update_department(department_id:int, department_details:schemas.Department,db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    department_query = db.query(models.Department).filter(models.Department.id == department_id)
    department = department_query.first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id: {department_id} does not exist")
    department_query.update(department_details.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Department updated successfully!"}


@router.delete('/{department_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id:int,db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    department_query = db.query(models.Department).filter(models.Department.id == department_id)
    department = department_query.first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id: {department_id} does not exist")
    department_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)