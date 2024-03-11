from fastapi import APIRouter, HTTPException, status, Depends
from .. import database, models, schemas, oauth2
from sqlalchemy.orm import Session

router = APIRouter(prefix="/leave_type", tags=["Leave Type"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.LeaveTypeOut
)
def create_leave_type(
    leave_type_details: schemas.LeaveType,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    new_leave_type = models.LeaveType(**leave_type_details.model_dump())
    db.add(new_leave_type)
    db.commit()
    db.refresh(new_leave_type)
    return new_leave_type


@router.get("/", response_model=list[schemas.LeaveTypeOut])
def get_leave_types(
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    leave_types = db.query(models.LeaveType).all()
    return leave_types


@router.get("/{leave_type_id}", response_model=schemas.LeaveTypeOut)
def get_leave_type(
    leave_type_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    leave_type = (
        db.query(models.LeaveType).filter(models.LeaveType.id == leave_type_id).first()
    )
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave Type not found!"
        )

    return leave_type
