from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ticket_response import TicketResponse
from app.schemas.ticket_response import TicketResponseCreate

from app.repositories.ticket_response_repository import (
    TicketResponseRepository
)

from app.repositories.ticket_repository import TicketRepository


class TicketResponseService:

    @staticmethod
    def check_ticket_access(
        ticket,
        current_user
    ):
        """
        Check whether the current user is allowed
        to access the ticket.
        """

        # Admin can access any ticket
        if current_user.role.value == "admin":
            return

        # Customer can access only their own tickets
        if current_user.role.value == "customer":

            if ticket.customer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this ticket"
                )

            return

        # Support agent can access only assigned tickets
        if current_user.role.value == "support_agent":

            if ticket.assigned_agent_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this ticket"
                )

            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket"
        )

    # ========================================================
    # CREATE RESPONSE
    # ========================================================

    @staticmethod
    def create_response(
        db: Session,
        ticket_id: int,
        user_id: int,
        data: TicketResponseCreate,
        current_user
    ) -> TicketResponse:

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        TicketResponseService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        response = TicketResponse(
            ticket_id=ticket_id,
            user_id=user_id,
            message=data.message
        )

        return TicketResponseRepository.create(
            db=db,
            response=response
        )

    # ========================================================
    # GET RESPONSES
    # ========================================================

    @staticmethod
    def get_ticket_responses(
        db: Session,
        ticket_id: int,
        current_user
    ):

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        TicketResponseService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        return TicketResponseRepository.get_by_ticket(
            db=db,
            ticket_id=ticket_id
        )