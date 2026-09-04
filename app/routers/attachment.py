from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.attachment import (
    AttachmentResponse
)

from app.services.attachment_service import (
    AttachmentService
)

from app.core.security import (
    get_current_user
)


router = APIRouter(
    tags=["Attachments"]
)


@router.post(
    "/tickets/{ticket_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await AttachmentService.create_attachment(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        file=file
    )


@router.get(
    "/tickets/{ticket_id}/attachments",
    response_model=list[AttachmentResponse]
)
def get_ticket_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return AttachmentService.get_ticket_attachments(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user
    )


@router.get(
    "/attachments/{attachment_id}"
)
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    attachment = AttachmentService.get_attachment(
        db=db,
        attachment_id=attachment_id,
        current_user=current_user
    )

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    AttachmentService.delete_attachment(
        db=db,
        attachment_id=attachment_id,
        current_user=current_user
    )

    return None