from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification

from app.repositories.notification_repository import (
    NotificationRepository
)


class NotificationService:

    # ========================================================
    # CREATE NOTIFICATION
    # ========================================================

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        message: str,
        ticket_id: int | None = None
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            ticket_id=ticket_id,
            message=message,
            is_read=False
        )

        return NotificationRepository.create(
            db=db,
            notification=notification
        )

    # ========================================================
    # GET MY NOTIFICATIONS
    # ========================================================

    @staticmethod
    def get_my_notifications(
        db: Session,
        user_id: int
    ):

        return NotificationRepository.get_by_user(
            db=db,
            user_id=user_id
        )

    # ========================================================
    # MARK ONE AS READ
    # ========================================================

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ):

        notification = NotificationRepository.get_by_id(
            db=db,
            notification_id=notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this notification"
            )

        return NotificationRepository.mark_as_read(
            db=db,
            notification=notification
        )

    # ========================================================
    # MARK ALL AS READ
    # ========================================================

    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: int
    ):

        NotificationRepository.mark_all_as_read(
            db=db,
            user_id=user_id
        )

        return {
            "message": "All notifications marked as read"
        }

    # ========================================================
    # DELETE NOTIFICATION
    # ========================================================

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ):

        notification = NotificationRepository.get_by_id(
            db=db,
            notification_id=notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this notification"
            )

        NotificationRepository.delete(
            db=db,
            notification=notification
        )