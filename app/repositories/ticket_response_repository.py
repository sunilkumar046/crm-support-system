from sqlalchemy.orm import Session

from app.models.ticket_response import TicketResponse


class TicketResponseRepository:

    @staticmethod
    def create(
        db: Session,
        response: TicketResponse
    ):
        db.add(response)
        db.commit()
        db.refresh(response)

        return response

    @staticmethod
    def get_by_ticket(
        db: Session,
        ticket_id: int
    ):
        return (
            db.query(TicketResponse)
            .filter(
                TicketResponse.ticket_id == ticket_id
            )
            .order_by(
                TicketResponse.created_at.asc()
            )
            .all()
        )