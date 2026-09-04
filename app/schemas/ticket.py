from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import (
    TicketPriority,
    TicketStatus
)


# ============================================================
# CREATE TICKET
# ============================================================

class TicketCreate(BaseModel):

    subject: str
    description: str
    category_id: int
    priority: TicketPriority = TicketPriority.MEDIUM


# ============================================================
# UPDATE TICKET
# ============================================================

class TicketUpdate(BaseModel):

    subject: str | None = None
    description: str | None = None
    category_id: int | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


# ============================================================
# ASSIGN TICKET
# ============================================================

class TicketAssign(BaseModel):

    agent_id: int


# ============================================================
# TICKET RESPONSE
# ============================================================

class TicketResponse(BaseModel):

    id: int
    customer_id: int

    subject: str
    description: str

    category_id: int

    priority: TicketPriority
    status: TicketStatus

    assigned_agent_id: int | None

    created_at: datetime
    updated_at: datetime | None
    resolved_at: datetime | None

    sla_deadline: datetime | None = None
    first_response_at: datetime | None = None
    resolution_time: datetime | None = None
    sla_status: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# ASSIGNMENT WORKLOAD RESPONSE
# ============================================================

class AgentWorkloadResponse(BaseModel):

    agent_id: int
    total_assigned: int
    open_tickets: int
    in_progress_tickets: int
    waiting_for_customer_tickets: int
    resolved_tickets: int
    critical_tickets: int