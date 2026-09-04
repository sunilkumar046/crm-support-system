from sqlalchemy.orm import Session

from app.models.sla_policy import SLAPolicy


class SLARepository:

    @staticmethod
    def get_by_priority(
        db: Session,
        priority: str
    ):

        return (
            db.query(SLAPolicy)
            .filter(
                SLAPolicy.priority == priority
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session
    ):

        return (
            db.query(SLAPolicy)
            .order_by(
                SLAPolicy.id
            )
            .all()
        )