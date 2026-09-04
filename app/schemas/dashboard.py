from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminDashboardResponse(BaseModel):

    total_customers: int
    total_support_agents: int
    total_tickets: int

    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    critical_tickets: int

    sla_breached_tickets: int

    average_resolution_hours: float


class AgentDashboardResponse(BaseModel):

    assigned_tickets: int

    open_tickets: int
    in_progress_tickets: int
    waiting_for_customer_tickets: int
    resolved_tickets: int

    critical_tickets: int
    sla_breached_tickets: int


class CustomerDashboardResponse(BaseModel):

    total_tickets: int

    open_tickets: int
    in_progress_tickets: int
    waiting_for_customer_tickets: int
    resolved_tickets: int
    closed_tickets: int

    recent_tickets: list


class RecentTicketResponse(BaseModel):

    id: int
    subject: str
    status: str
    priority: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )