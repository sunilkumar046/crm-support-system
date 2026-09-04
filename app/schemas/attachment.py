from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: int
    ticket_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )