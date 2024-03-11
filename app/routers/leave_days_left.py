from fastapi import APIRouter, HTTPException, status, Depends
from .. import database, models, schemas, oauth2
from sqlalchemy.orm import Session

router = APIRouter(prefix="/leave_days_left", tags=["Leave Days Left"])


@router.get("/", response_model=list[schemas.LeaveDaysLeft])
def get_leave_days_left(
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You do not have an employee profile",
        )
    leave_days_left = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == employee.id,
    )
    return leave_days_left
