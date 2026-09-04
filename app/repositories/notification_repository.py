from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    # ========================================================
    # CREATE
    # ========================================================

    @staticmethod
    def create(
        db: Session,
        notification: Notification
    ):

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    # ========================================================
    # GET USER NOTIFICATIONS
    # ========================================================

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id
            )
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # GET SINGLE NOTIFICATION
    # ========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        notification_id: int
    ):

        return (
            db.query(Notification)
            .filter(
                Notification.id == notification_id
            )
            .first()
        )

    # ========================================================
    # MARK AS READ
    # ========================================================

    @staticmethod
    def mark_as_read(
        db: Session,
        notification: Notification
    ):

        notification.is_read = True

        db.commit()
        db.refresh(notification)

        return notification

    # ========================================================
    # MARK ALL AS READ
    # ========================================================

    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: int
    ):

        (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .update(
                {
                    Notification.is_read: True
                },
                synchronize_session=False
            )
        )

        db.commit()

    # ========================================================
    # DELETE
    # ========================================================

    @staticmethod
    def delete(
        db: Session,
        notification: Notification
    ):

        db.delete(notification)
        db.commit()