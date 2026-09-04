from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketResponseCreate(BaseModel):
    message: str


class TicketResponseResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )