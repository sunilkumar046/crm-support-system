from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:

    @staticmethod
    def create(
        db: Session,
        attachment: Attachment
    ):
        db.add(attachment)
        db.commit()
        db.refresh(attachment)

        return attachment

    @staticmethod
    def get_by_id(
        db: Session,
        attachment_id: int
    ):
        return (
            db.query(Attachment)
            .filter(
                Attachment.id == attachment_id
            )
            .first()
        )

    @staticmethod
    def get_by_ticket(
        db: Session,
        ticket_id: int
    ):
        return (
            db.query(Attachment)
            .filter(
                Attachment.ticket_id == ticket_id
            )
            .order_by(
                Attachment.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        attachment: Attachment
    ):
        db.delete(attachment)
        db.commit()