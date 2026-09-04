from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.security import get_current_user

from app.schemas.notification import (
    NotificationResponse
)

from app.services.notification_service import (
    NotificationService
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NotificationService.get_my_notifications(
        db=db,
        user_id=current_user.id
    )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )


@router.put(
    "/read-all"
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NotificationService.mark_all_as_read(
        db=db,
        user_id=current_user.id
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    return None