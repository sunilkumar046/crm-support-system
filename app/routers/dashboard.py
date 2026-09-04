from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.security import (
    require_role
)

from app.schemas.dashboard import (
    AdminDashboardResponse,
    AgentDashboardResponse,
    CustomerDashboardResponse
)

from app.services.dashboard_service import (
    DashboardService
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/admin",
    response_model=AdminDashboardResponse
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return DashboardService.get_admin_dashboard(
        db=db,
        current_user=current_user
    )


@router.get(
    "/agent",
    response_model=AgentDashboardResponse
)
def get_agent_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("support_agent")
    )
):

    return DashboardService.get_agent_dashboard(
        db=db,
        current_user=current_user
    )


@router.get(
    "/customer",
    response_model=CustomerDashboardResponse
)
def get_customer_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("customer")
    )
):

    return DashboardService.get_customer_dashboard(
        db=db,
        current_user=current_user
    )