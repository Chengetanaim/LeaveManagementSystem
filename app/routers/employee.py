from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List

router = APIRouter(prefix='/employees', tags=['Employees'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.EmployeeOut)
def create_employee(employee_details:schemas.EmployeeCreate, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if employee:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'You already have an employee profile')
    department = db.query(models.Department).filter(models.Department.id == employee_details.department_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'There is no department of id: {employee_details.department_id}')
    new_employee = models.Employee(**employee_details.dict(), user_id=current_user.id)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get('/', response_model=List[schemas.EmployeeOut])
def get_employees(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employees = db.query(models.Employee).all()
    return employees

@router.get('/{employee_id}', response_model=schemas.EmployeeOut)
def get_employee(employee_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id: {employee_id} does not exist.")
    return employee

@router.put('/{employee_id}')
def update_employee(employee_id:int, employee_details:schemas.EmployeeCreate, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_query= db.query(models.Employee).filter(models.Employee.id == employee_id)
    employee = employee_query.first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id: {employee_id} does not exist.")
    if current_user.id != employee.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permissions to update profile")
    department = db.query(models.Department).filter(models.Department.id == employee_details.department_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'There is no department of id: {employee_details.department_id}')
    employee_query.update(employee_details.dict(), synchronize_session=False)
    db.commit()
    return {"data": "Profile successfully updated"}


@router.delete('/{employee_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_query= db.query(models.Employee).filter(models.Employee.id == employee_id)
    employee = employee_query.first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id: {employee_id} does not exist.")
    if current_user.id != employee.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permissions to delete profile")
    employee_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)