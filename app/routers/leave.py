from datetime import timedelta
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy import func, select, desc
from sqlalchemy.orm import Session

from app.errors import Error400, Error404
from .. import database, models, oauth2, schemas
from typing import List
from fastapi.responses import Response

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/", response_model=schemas.LeaveOut)
def create_leave(
    leave_details: schemas.Leave,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if employee is None:
        raise Error404(message="employee is not found.")

    leave_type = (
        db.query(models.LeaveType)
        .filter(models.LeaveType.id == leave_details.leave_type_id)
        .first()
    )
    if leave_type is None:
        raise Error404(message="leave type is not found.")

    leave_days = leave_details.end_date.date() - leave_details.start_date.date()
    if leave_type.leave_type == "Annual leave":
        grade = (
            db.query(models.Grade).filter(models.Grade.id == employee.grade_id).first()
        )
        if grade is None:
            raise Error404(message="grade is not found.")

        employee_grade = (
            db.query(models.EmployeeGrade)
            .filter(
                models.EmployeeGrade.grade_id == employee.grade_id,
                models.EmployeeGrade.employee_id == employee.id,
            )
            .first()
        )

        new_leave = models.Leave(
            **leave_details.model_dump(), status="pending", employee_id=employee.id
        )
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
        return new_leave

    new_leave = models.Leave(
        **leave_details.model_dump(), status="pending", employee_id=employee.id
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave


@router.get("/", response_model=List[schemas.LeaveOut])
def get_leaves(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    employee = db.query(models.Employee).filter_by(user_id=current_user.id).first()
    if employee is None:
        raise Error404("Not employee was found.")

    leaves = (
        db.query(models.Leave)
        .filter(models.Leave.employee_id == employee.id)
        .order_by(desc(models.Leave.start_date), desc(models.Leave.end_date))
        .all()
    )
    return leaves


@router.get("/{leave_id}", response_model=schemas.LeaveOut)
def get_leave(
    leave_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if leave is None:
        raise Error404("Leave is not found.")

    return leave


@router.put("/{leave_id}")
def update_leave(
    leave_id: int,
    leave_details: schemas.Leave,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )

    leave_query = db.query(models.Leave).filter(models.Leave.id == leave_id)
    leave = leave_query.first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )
    leave_query.update(**leave_details.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Successfully updated"}


@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(
    leave_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    leave_query = db.query(models.Leave).filter(models.Leave.id == leave_id)
    leave = leave_query.first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )
    leave_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/approve_leave/{leave_id}")
def approve_leave(
    leave_id: int,
    status_details: schemas.Status,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    leave_query = db.query(models.Leave).filter_by(id=leave_id)

    leave = leave_query.first()
    if leave is None:
        raise Error404(f"Leave with id {leave_id} does not exist.")

    employee = (
        db.query(models.Employee)
        .filter(models.Employee.id == leave.employee_id)
        .first()
    )
    if employee is None:
        raise Error404("Employee associated with the leave is not found")

    leave_type = (
        db.query(models.LeaveType)
        .filter(models.LeaveType.id == leave.leave_type_id)
        .first()
    )
    if leave_type is None:
        raise Error404("There is no leave type associated with the leave")

    leave_days = leave.end_date.date() - leave.start_date.date()
    leave_days_left_query = db.query(models.LeaveDaysLeft).filter(
        models.LeaveDaysLeft.employee_id == employee.id,
        models.LeaveDaysLeft.leave_type_id == leave_type.id,
    )

    leave_days_left = leave_days_left_query.first()
    if leave_days_left:
        if leave_days > timedelta(days=float(leave_days_left.days_left)):
            raise Error400(
                "Leave days requested are greater than the leave days left.",
            )

    if leave_days > timedelta(days=float(leave_type.leave_days)):
        raise Error400("Leave days requested are greater than the leave days left.")

    if status_details.value == "approved":
        if leave_type.leave_type == "Annual leave":
            grade = (
                db.query(models.Grade)
                .filter(models.Grade.id == employee.grade_id)
                .first()
            )
            if grade is None:
                raise Error404("There are no grades associated with the employee")

            employee_grade_query = db.query(models.EmployeeGrade).filter(
                models.EmployeeGrade.grade_id == employee.grade_id,
                models.EmployeeGrade.employee_id == employee.id,
            )

            employee_grade = employee_grade_query.first()
            if not employee_grade:
                if leave_days > timedelta(days=float(grade.leave_days)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Leave days requested are greater than the leave days left",
                    )
            else:
                if leave_days > timedelta(days=float(employee_grade.days_left)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Leave days requested are greater than the leave days left",
                    )
            if employee_grade:
                days_left = timedelta(days=float(employee_grade.days_left)) - leave_days
                employee_grade_query.update(
                    {"days_left": days_left.days}, synchronize_session=False
                )
                db.commit()
                leave_query.update(
                    {"status": status_details.value}, synchronize_session=False
                )
                db.commit()

                return {
                    "message": f"Leave status successfully updated to {status_details.value}"
                }

            else:
                days_left = timedelta(days=float(grade.leave_days)) - leave_days
                new_employee_grade = models.EmployeeGrade(
                    grade_id=grade.id, employee_id=employee.id, days_left=days_left.days
                )
                db.add(new_employee_grade)
                db.commit()
                db.refresh(new_employee_grade)

                leave_query.update(
                    {"status": status_details.value}, synchronize_session=False
                )
                db.commit()

                return {
                    "message": f"Leave status successfully updated to {status_details.value}"
                }

        if leave_days_left:
            days_left = timedelta(days=float(leave_days_left.days_left)) - leave_days
            leave_days_left_query.update(
                {"days_left": days_left.days}, synchronize_session=False
            )
            db.commit()
        else:
            days_left = timedelta(days=float(leave_type.leave_days)) - leave_days
            new_leave_days_left = models.LeaveDaysLeft(
                employee_id=employee.id,
                leave_type_id=leave_type.id,
                days_left=days_left.days,
            )

            db.add(new_leave_days_left)
            db.commit()
            db.refresh(new_leave_days_left)
    leave_query.update({"status": status_details.value}, synchronize_session=False)
    db.commit()

    return {"message": f"Leave status successfully updated to {status_details.value}"}
