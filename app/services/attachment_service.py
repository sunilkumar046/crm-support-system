import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.models.ticket import Ticket

from app.repositories.attachment_repository import (
    AttachmentRepository
)

from app.repositories.ticket_repository import (
    TicketRepository
)


class AttachmentService:

    MAX_FILE_SIZE = 5 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".doc",
        ".docx",
        ".txt"
    }

    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    }

    UPLOAD_DIRECTORY = Path("uploads") / "tickets"

    @staticmethod
    def check_ticket_access(
        ticket: Ticket,
        current_user
    ):
        role = current_user.role.value

        # Admin can access everything
        if role == "admin":
            return

        # Customer can access only own ticket
        if role == "customer":
            if ticket.customer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this ticket"
                )
            return

        # Support agent can access only assigned ticket
        if role == "support_agent":
            if ticket.assigned_agent_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this ticket"
                )
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket"
        )

    @staticmethod
    def check_ticket_modification_allowed(
        ticket: Ticket
    ):
        status_value = ticket.status.value

        if status_value in {
            "closed",
            "cancelled"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachments cannot be modified for closed or cancelled tickets"
            )

    @staticmethod
    async def create_attachment(
        db: Session,
        ticket_id: int,
        current_user,
        file: UploadFile
    ) -> Attachment:

        # Find ticket
        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        # Check authorization
        AttachmentService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        # Closed/cancelled tickets cannot be modified
        AttachmentService.check_ticket_modification_allowed(
            ticket=ticket
        )

        # Validate filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required"
            )

        original_filename = Path(file.filename).name

        # Validate extension
        extension = Path(
            original_filename
        ).suffix.lower()

        if extension not in AttachmentService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Unsupported file type. "
                    "Allowed types: PDF, JPG, JPEG, PNG, DOC, DOCX, TXT"
                )
            )

        # Validate content type
        if (
            file.content_type
            and file.content_type
            not in AttachmentService.ALLOWED_CONTENT_TYPES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file content type"
            )

        # Read file
        file_content = await file.read()

        file_size = len(file_content)

        # Validate size
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty files are not allowed"
            )

        if file_size > AttachmentService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 5 MB"
            )

        # Create directory
        ticket_directory = (
            AttachmentService.UPLOAD_DIRECTORY
            / str(ticket_id)
        )

        ticket_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # Generate unique file name
        unique_filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        file_path = (
            ticket_directory
            / unique_filename
        )

        # Save file
        try:
            with open(
                file_path,
                "wb"
            ) as output_file:
                output_file.write(file_content)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )

        # Database path
        database_file_path = str(
            file_path
        ).replace("\\", "/")

        attachment = Attachment(
            ticket_id=ticket_id,
            uploaded_by=current_user.id,
            file_name=original_filename,
            file_path=database_file_path,
            file_size=file_size,
            file_type=file.content_type or extension
        )

        try:
            return AttachmentRepository.create(
                db=db,
                attachment=attachment
            )

        except Exception:
            # Remove physical file if database insert fails
            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save attachment information"
            )

    @staticmethod
    def get_ticket_attachments(
        db: Session,
        ticket_id: int,
        current_user
    ):

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        AttachmentService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        return AttachmentRepository.get_by_ticket(
            db=db,
            ticket_id=ticket_id
        )

    @staticmethod
    def get_attachment(
        db: Session,
        attachment_id: int,
        current_user
    ):

        attachment = AttachmentRepository.get_by_id(
            db=db,
            attachment_id=attachment_id
        )

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=attachment.ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        AttachmentService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        file_path = Path(
            attachment.file_path
        )

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment file not found"
            )

        return attachment

    @staticmethod
    def delete_attachment(
        db: Session,
        attachment_id: int,
        current_user
    ):

        attachment = AttachmentRepository.get_by_id(
            db=db,
            attachment_id=attachment_id
        )

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=attachment.ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        AttachmentService.check_ticket_access(
            ticket=ticket,
            current_user=current_user
        )

        AttachmentService.check_ticket_modification_allowed(
            ticket=ticket
        )

        file_path = Path(
            attachment.file_path
        )

        # Delete database record
        AttachmentRepository.delete(
            db=db,
            attachment=attachment
        )

        # Delete physical file
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass