from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import database, models, schemas, oauth2
from app.errors import Error404

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

    if employee is None:
        raise Error404("Employee is not found.")

    type_of_leaves = db.query(models.LeaveType).all()
    leaves_by_type = (
        db.query(models.Leave)
        .filter_by(employee_id=employee.id)
        .group_by(models.Leave.leave_type_id, models.Leave.id)
        .all()
    )

    days_used = sum(
        [(leave.end_date - leave.start_date).days for leave in leaves_by_type]
    )
    print(days_used)

    employee_leaves: list[dict[str, str | int]] = []
    for leave_type in type_of_leaves:
        employee_leave: dict[str, str | int] = {}
        employee_leave["type"] = str(leave_type.leave_type)
        employee_leave["days"] = int(leave_type.leave_days)
        employee_leave["days_left"] = 10
        employee_leaves.append(employee_leave)

    print(employee_leaves)

    leave_days_left = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == employee.id,
    )
    return leave_days_left
