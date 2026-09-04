from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    status,
    HTTPException
)

from app.models.customer import Customer

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketAssign,
    AgentWorkloadResponse
)

from app.services.ticket_service import TicketService

from app.core.security import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# ============================================================
# CREATE TICKET
# ============================================================

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    data: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("customer", "admin")
    )
):

    # Find the Customer record using the logged-in User ID
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    # Make sure the customer profile exists
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    return TicketService.create_ticket(
        db=db,
        customer_id=customer.id,
        data=data,
        background_tasks=background_tasks
    )


# ============================================================
# GET ALL TICKETS
# ============================================================

@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "support_agent"
        )
    )
):

    return TicketService.get_all_tickets(
        db
    )


# ============================================================
# GET MY TICKETS
# ============================================================

@router.get(
    "/my",
    response_model=list[TicketResponse]
)
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "customer",
            "admin"
        )
    )
):

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    return TicketService.get_customer_tickets(
        db=db,
        customer_id=customer.id
    )


# ============================================================
# GET MY ASSIGNED TICKETS
# Support Agent
# ============================================================

@router.get(
    "/assigned",
    response_model=list[TicketResponse]
)
def get_assigned_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("support_agent")
    )
):

    return TicketService.get_assigned_tickets(
        db=db,
        agent_id=current_user.id
    )


# ============================================================
# GET UNASSIGNED TICKETS
# Admin and Support Agent
# ============================================================

@router.get(
    "/unassigned",
    response_model=list[TicketResponse]
)
def get_unassigned_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "support_agent"
        )
    )
):

    return TicketService.get_unassigned_tickets(
        db
    )


# ============================================================
# ASSIGN / REASSIGN TICKET
# Admin and Support Agent
# ============================================================

@router.post(
    "/{ticket_id}/assign",
    response_model=TicketResponse
)
def assign_ticket(
    ticket_id: int,
    data: TicketAssign,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "support_agent"
        )
    )
):

    return TicketService.assign_ticket(
        db=db,
        ticket_id=ticket_id,
        agent_id=data.agent_id,
        background_tasks=background_tasks
    )


# ============================================================
# AGENT WORKLOAD
# Admin
# ============================================================

@router.get(
    "/workload",
    response_model=list[AgentWorkloadResponse]
)
def get_agent_workload(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return TicketService.get_all_agent_workload(
        db=db
    )


# ============================================================
# SINGLE AGENT WORKLOAD
# Admin
# ============================================================

@router.get(
    "/workload/{agent_id}",
    response_model=AgentWorkloadResponse
)
def get_single_agent_workload(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return TicketService.get_agent_workload(
        db=db,
        agent_id=agent_id
    )


# ============================================================
# GET SINGLE TICKET
# ============================================================

@router.get(
    "/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return TicketService.get_ticket(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user
    )


# ============================================================
# UPDATE TICKET
# ============================================================

@router.put(
    "/{ticket_id}",
    response_model=TicketResponse
)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "support_agent"
        )
    )
):

    return TicketService.update_ticket(
        db=db,
        ticket_id=ticket_id,
        data=data,
        current_user=current_user,
        background_tasks=background_tasks
    )


# ============================================================
# DELETE TICKET
# ============================================================

@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    TicketService.delete_ticket(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user
    )

    return None