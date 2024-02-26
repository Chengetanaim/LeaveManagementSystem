from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix='/employee_grades', tags=['Employee Grades'])

@router.post('/', response_model=schemas.EmployeeGrade, status_code=status.HTTP_201_CREATED)
def create_employee_grade(employee_grade_details:schemas.EmployeeGrade, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_grade = db.query(models.EmployeeGrade).filter(models.EmployeeGrade.grade_id == employee_grade_details.grade_id, models.EmployeeGrade.employee_id == employee_grade_details.employee_id).first()
    if employee_grade:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Employee of id: {employee_grade_details.employee_id} already has a grade")
    employee = db.query(models.Employee).filter(models.Employee.id == employee_grade_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee of id: {employee_grade_details.employee_id} does not exist.")
    grade = db.query(models.Grade).filter(models.Grade.id == employee_grade_details.grade_id).first()
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grade of id: {employee_grade_details.grade_id} does not exist.")
    new_employee_grade = models.EmployeeGrade(**employee_grade_details.dict())
    db.add(new_employee_grade)
    db.commit()
    db.refresh(new_employee_grade)
    return new_employee_grade

@router.get('/', response_model=List[schemas.EmployeeGrade])
def get_employee_grades(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_grades = db.query(models.EmployeeGrade).all()
    return employee_grades

@router.get('/{employee_id}', response_model=schemas.EmployeeGrade)
def get_employee_grade(employee_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_grade = db.query(models.EmployeeGrade).filter(models.EmployeeGrade.employee_id == employee_id).first()
    if not employee_grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record found")
    return employee_grade


@router.put('/{employee_id}')
def update_employee_grade(employee_id:int, employee_grade_details:schemas.EmployeeGrade,db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_grade_query = db.query(models.EmployeeGrade).filter(models.EmployeeGrade.employee_id == employee_id)
    employee_grade = employee_grade_query.first()
    if not employee_grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record to update")
    
    employee_grade = db.query(models.EmployeeGrade).filter(models.EmployeeGrade.grade_id == employee_grade_details.grade_id, models.EmployeeGrade.employee_id == employee_grade_details.employee_id).first()
    if employee_grade:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Employee of id: {employee_grade_details.employee_id} already has a grade")
    employee = db.query(models.Employee).filter(models.Employee.id == employee_grade_details.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee of id: {employee_grade_details.employee_id} does not exist.")
    grade = db.query(models.Grade).filter(models.Grade.id == employee_grade_details.grade_id).first()
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grade of id: {employee_grade_details.grade_id} does not exist.")
    employee_grade_query.update(employee_grade_details.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Employee grade updated successfully"}


@router.delete('/{employee_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_grade(employee_id:int,db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    employee_grade_query = db.query(models.EmployeeGrade).filter(models.EmployeeGrade.employee_id == employee_id)
    employee_grade = employee_grade_query.first()
    if not employee_grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record to update")
    employee_grade_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
