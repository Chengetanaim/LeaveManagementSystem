from datetime import datetime
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
    employee = db.query(models.Employee).filter_by(user_id=current_user.id).first()
    if employee is None:
        raise Error404(f"Employee with user id {current_user.id} not found.")

    leave_types = db.query(models.LeaveType).all()
    leaves_by_type = (
        db.query(models.Leave)
        .filter(
            models.Leave.employee_id == employee.id,
            models.Leave.status == schemas.Status.approved,
        )
        .group_by(models.Leave.leave_type_id)
        .with_entities(
            models.Leave.leave_type_id,
            func.sum(models.Leave.end_date - models.Leave.start_date).label(
                "days_used"
            ),
        )
        .all()
    )

    employee_leaves: list[dict[str, str | int]] = []

    for leave_type in leave_types:
        employee_leave: dict[str, str | int] = {}

        employee_leave["type"] = str(leave_type.leave_type)
        employee_leave["days"] = int(leave_type.leave_days)

        if len(leaves_by_type) == 0:
            employee_leave["days_used"] = 0

        else:
            employee_record = tuple(
                filter(lambda x: x[0] == leave_type.id, leaves_by_type)
            )[0]

            if len(employee_record) == 0:
                employee_leave["days_used"] = 0
            else:
                (_, employee_leave_days_used) = employee_record
                employee_leave["days_used"] = employee_leave_days_used.days

        employee_leaves.append(employee_leave)
    return employee_leaves
