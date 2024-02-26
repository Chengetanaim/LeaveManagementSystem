from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix='/grades', tags=['Grades'])

@router.post('/', response_model=schemas.GradeOut, status_code=status.HTTP_201_CREATED)
def create_grade(grade_details:schemas.Grade, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    new_grade = models.Grade(**grade_details.dict())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade

@router.get('/', response_model=List[schemas.GradeOut])
def get_grades(db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    grades = db.query(models.Grade).all()
    return grades

@router.get('/{grade_id}', response_model=schemas.GradeOut)
def get_grade(grade_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grade with id: {grade_id} does not exist.")
    return grade

@router.put('/{grade_id}')
def update_grade(grade_id:int, grade_details:schemas.Grade, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    grade_query = db.query(models.Grade).filter(models.Grade.id == grade_id)
    grade = grade_query.first()
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grade with id: {grade_id} does not exist.")
    grade_query.update(grade_details.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Grade has been successfully updated"}

@router.delete('/{grade_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(grade_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(oauth2.get_current_user)):
    grade_query = db.query(models.Grade).filter(models.Grade.id == grade_id)
    grade = grade_query.first()
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grade with id: {grade_id} does not exist.")
    grade_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    