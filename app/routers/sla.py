from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.security import (
    get_current_user
)

from app.services.sla_service import (
    SLAService
)

from app.schemas.sla import (
    SLAResponse
)


router = APIRouter(
    prefix="/sla",
    tags=["SLA"]
)


@router.get(
    "/tickets",
    response_model=list[SLAResponse]
)
def get_sla_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return SLAService.get_all_sla_tickets(
        db=db
    )


@router.get(
    "/breached",
    response_model=list[SLAResponse]
)
def get_breached_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return SLAService.get_breached_tickets(
        db=db
    )


@router.get(
    "/at-risk",
    response_model=list[SLAResponse]
)
def get_at_risk_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return SLAService.get_at_risk_tickets(
        db=db
    )