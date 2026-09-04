from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.ticket_response import (
    TicketResponseCreate,
    TicketResponseResponse
)

from app.services.ticket_response_service import (
    TicketResponseService
)

from app.core.security import get_current_user


router = APIRouter(
    prefix="/tickets",
    tags=["Ticket Responses"]
)


# ============================================================
# ADD RESPONSE TO TICKET
# ============================================================

@router.post(
    "/{ticket_id}/responses",
    response_model=TicketResponseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket_response(
    ticket_id: int,
    data: TicketResponseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return TicketResponseService.create_response(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        data=data,
        current_user=current_user
    )


# ============================================================
# GET TICKET RESPONSES
# ============================================================

@router.get(
    "/{ticket_id}/responses",
    response_model=list[TicketResponseResponse]
)
def get_ticket_responses(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return TicketResponseService.get_ticket_responses(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user
    )