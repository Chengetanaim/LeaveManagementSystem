from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2

router = APIRouter(prefix="/sell-leave", tags=["Sell Leave"])


class Error404(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


@router.post("/", status_code=status.HTTP_201_CREATED)
def sell_leave(
    sell_leave_details: schemas.SellLeave,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    employee_sending_leave = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )

    if not employee_sending_leave:
        raise Error404(message="User does not have employee details")

    employee_receiving_leave = (
        db.query(models.Employee)
        .filter(models.Employee.id == sell_leave_details.employee_id)
        .first()
    )

    if not employee_receiving_leave:
        raise Error404(message="Receiving Employee does not exist")

    leave_type_to_sell = (
        db.query(models.LeaveType)
        .filter(models.LeaveType.id == sell_leave_details.leave_type_id)
        .first()
    )

    if not leave_type_to_sell:
        raise Error404(message="Leave type does not exist")

    if leave_type_to_sell.leave_type == "Annual leave":
        employee_sending_leave_grade = (
            db.query(models.EmployeeGrade)
            .filter(
                models.EmployeeGrade.grade_id == employee_sending_leave.grade_id,
                models.EmployeeGrade.employee_id == employee_sending_leave.id,
            )
            .first()
        )

        if employee_sending_leave_grade is None:
            raise Error404(message="Employee does not have a grade")

        current_grade = (
            db.query(models.Grade)
            .filter(models.Grade.id == employee_sending_leave.grade_id)
            .first()
        )

        employee_receiving_leave_grade = (
            db.query(models.EmployeeGrade)
            .filter(
                models.EmployeeGrade.grade_id == employee_receiving_leave.grade_id,
                models.EmployeeGrade.employee_id == employee_receiving_leave.id,
            )
            .first()
        )

        target_grade = (
            db.query(models.Grade)
            .filter(models.Grade.id == employee_receiving_leave.grade_id)
            .first()
        )

        if employee_sending_leave_grade:
            days_left = (
                employee_sending_leave_grade.days_left
                - sell_leave_details.number_of_days
            )
            if days_left < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
                )
            employee_sending_leave_grade.update(
                {"days_left": days_left}, synchronize_session=False
            )
            db.commit()
        else:

            days_left = current_grade.leave_days - sell_leave_details.number_of_days
            if days_left < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
                )
            new_current_employee_grade = models.EmployeeGrade(
                employee_id=employee_sending_leave.id,
                grade_id=current_grade.id,
                days_left=days_left,
            )
            db.add(new_current_employee_grade)
            db.commit()
            db.refresh(new_current_employee_grade)
        if employee_receiving_leave_grade:
            employee_receiving_leave_grade.update(
                {
                    "days_left": employee_receiving_leave_grade.days_left
                    + sell_leave_details.number_of_days
                },
                synchronize_session=False,
            )
            db.commit()
        else:
            new_target_employee_grade = models.EmployeeGrade(
                employee_id=employee_receiving_leave.id,
                grade_id=target_grade.id,
                days_left=target_grade.leave_days + sell_leave_details.number_of_days,
            )
            db.add(new_target_employee_grade)
            db.commit()
            db.refresh(new_target_employee_grade)
        return {"message": "Annual Leave has been sold."}

    current_employee_leave_query = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == employee_sending_leave.id,
        models.LeaveDaysLeft.leave_type_id == leave_type_to_sell.id,
    )

    current_employee_leave = current_employee_leave_query.first()

    target_employee_leave_query = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == employee_receiving_leave.id,
        models.LeaveDaysLeft.leave_type_id == leave_type_to_sell.id,
    )
    target_employee_leave = target_employee_leave_query.first()

    if current_employee_leave:
        days_left = current_employee_leave.days_left - sell_leave_details.number_of_days
        if days_left < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
            )
        current_employee_leave_query.update(
            {"days_left": days_left}, synchronize_session=False
        )
        db.commit()
    else:
        days_left = leave_type_to_sell.leave_days - sell_leave_details.number_of_days
        if days_left < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
            )
        new_current_employee_leave = models.LeaveDaysLeft(
            employee_id=employee_sending_leave.id,
            leave_type_id=leave_type_to_sell.id,
            days_left=days_left,
        )
        db.add(new_current_employee_leave)
        db.commit()
        db.refresh(new_current_employee_leave)

    if target_employee_leave:
        target_employee_leave_query.update(
            {
                "days_left": target_employee_leave.days_left
                + sell_leave_details.number_of_days
            },
            synchronize_session=False,
        )
        db.commit()
    else:
        new_target_employee_leave = models.LeaveDaysLeft(
            employee_id=employee_receiving_leave.id,
            leave_type_id=leave_type_to_sell.id,
            days_left=leave_type_to_sell.leave_days + sell_leave_details.number_of_days,
        )
        db.add(new_target_employee_leave)
        db.commit()
        db.refresh(new_target_employee_leave)
    return new_current_employee_leave
