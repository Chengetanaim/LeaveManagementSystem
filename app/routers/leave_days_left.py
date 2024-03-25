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
        raise Error404(f"Employee with user id {current_user.id} not found.")

    type_of_leaves = db.query(models.LeaveType).all()
    leaves_by_type = (
        db.query(models.Leave)
        .filter_by(employee_id=employee.id)
        .group_by(models.Leave.leave_type_id, models.Leave.id)
        .all()
    )

    leaves_by_type = (
        db.query(models.Leave)
        .filter_by(employee_id=employee.id)
        .group_by(models.Leave.leave_type_id)
        .with_entities(
            models.Leave.leave_type_id,
            func.sum(models.Leave.end_date - models.Leave.start_date).label(
                "days_used"
            ),
        )
        .all()
    )

    print(leaves_by_type)
    FIRST_ITEM_ONTHE_TUPLE_IS_LEAVE_TYPE_ID = 0
    SECOND_ITEM_ONTHE_TUPLE_IS_DAYS_USED = 1

    employee_leaves: list[dict[str, str | int]] = []
    for leave_type in type_of_leaves:
        employee_leave: dict[str, str | int] = {}
        employee_leave["type"] = str(leave_type.leave_type)
        employee_leave["days"] = int(leave_type.leave_days)
        employee_leave["days_used"] = (
            0
            if len(leaves_by_type) == 0
            else [
                out_leave_type[SECOND_ITEM_ONTHE_TUPLE_IS_DAYS_USED]
                for out_leave_type in leaves_by_type
                if out_leave_type[FIRST_ITEM_ONTHE_TUPLE_IS_LEAVE_TYPE_ID]
                == leave_type.id
            ][0].days
        )
        employee_leaves.append(employee_leave)

    return employee_leaves
