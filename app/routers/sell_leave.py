from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2

router = APIRouter(prefix="/sell-leave", tags=["Sell Leave"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def sell_leave(
    sell_leave_details: schemas.SellLeave,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    current_employee = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have an employee profile.",
        )
    target_employee = (
        db.query(models.Employee)
        .filter(models.Employee.id == sell_leave_details.employee_id)
        .first()
    )
    if not target_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee does not exist."
        )
    leave_type = (
        db.query(models.LeaveType)
        .filter(models.LeaveType.id == sell_leave_details.leave_type_id)
        .first()
    )
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave does not exist"
        )
    if leave_type.leave_type == "Annual leave":
        current_employee_grade_query = db.query(models.EmployeeGrade).filter(
            models.EmployeeGrade.grade_id == current_employee.grade_id,
            models.EmployeeGrade.employee_id == current_employee.id,
        )
        current_employee_grade = current_employee_grade_query.first()
        target_employee_grade_query = db.query(models.EmployeeGrade).filter(
            models.EmployeeGrade.grade_id == target_employee.grade_id,
            models.EmployeeGrade.employee_id == target_employee.id,
        )
        target_employee_grade = target_employee_grade_query.first()
        current_grade = (
            db.query(models.Grade)
            .filter(models.Grade.id == current_employee.grade_id)
            .first()
        )
        target_grade = (
            db.query(models.Grade)
            .filter(models.Grade.id == target_employee.grade_id)
            .first()
        )
        if current_employee_grade:
            days_left = (
                current_employee_grade.days_left - sell_leave_details.number_of_days
            )
            if days_left < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
                )
            current_employee_grade_query.update(
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
                employee_id=current_employee.id,
                grade_id=current_grade.id,
                days_left=days_left,
            )
            db.add(new_current_employee_grade)
            db.commit()
            db.refresh(new_current_employee_grade)
        if target_employee_grade:
            target_employee_grade_query.update(
                {
                    "days_left": target_employee_grade.days_left
                    + sell_leave_details.number_of_days
                },
                synchronize_session=False,
            )
            db.commit()
        else:
            new_target_employee_grade = models.EmployeeGrade(
                employee_id=target_employee.id,
                grade_id=target_grade.id,
                days_left=target_grade.leave_days + sell_leave_details.number_of_days,
            )
            db.add(new_target_employee_grade)
            db.commit()
            db.refresh(new_target_employee_grade)
        return {"message": "Annual Leave has been sold."}
    current_employee_leave_query = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == current_employee.id,
        models.LeaveDaysLeft.leave_type_id == leave_type.id,
    )
    current_employee_leave = current_employee_leave_query.first()

    target_employee_leave_query = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == target_employee.id,
        models.LeaveDaysLeft.leave_type_id == leave_type.id,
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
        days_left = leave_type.leave_days - sell_leave_details.number_of_days
        if days_left < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operation cannot be peroformed, you will have remaining balance of {days_left} leave days left",
            )
        new_current_employee_leave = models.LeaveDaysLeft(
            employee_id=current_employee.id,
            leave_type_id=leave_type.id,
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
            employee_id=target_employee.id,
            leave_type_id=leave_type.id,
            days_left=leave_type.leave_days + sell_leave_details.number_of_days,
        )
        db.add(new_target_employee_leave)
        db.commit()
        db.refresh(new_target_employee_leave)
    return {"message": "Leave days successfully sold!"}
