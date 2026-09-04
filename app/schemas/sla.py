from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SLAResponse(BaseModel):

    ticket_id: int

    priority: str

    sla_deadline: datetime | None

    first_response_at: datetime | None

    resolution_time: datetime | None

    sla_status: str

    model_config = ConfigDict(
        from_attributes=True
    )