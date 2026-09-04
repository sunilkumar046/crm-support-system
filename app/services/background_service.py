from app.database.database import SessionLocal

from app.services.notification_service import (
    NotificationService
)


class BackgroundService:

    # ========================================================
    # CREATE NOTIFICATION BACKGROUND TASK
    # ========================================================

    @staticmethod
    def create_notification_task(
        user_id: int,
        message: str,
        ticket_id: int | None = None
    ):
        """
        Creates a notification using a new database session.

        Background tasks should not reuse the request's
        database session.
        """

        db = SessionLocal()

        try:

            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                message=message,
                ticket_id=ticket_id
            )

        finally:

            db.close()