from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

from app.repositories.audit_log_repository import (
    AuditLogRepository
)


class AuditLogService:

    @staticmethod
    def create_log(
        db: Session,
        user_id: int | None,
        action: str,
        entity: str,
        entity_id: int,
        previous_value: str | None = None,
        new_value: str | None = None
    ):

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            previous_value=previous_value,
            new_value=new_value
        )

        return AuditLogRepository.create(
            db=db,
            audit_log=audit_log
        )

    @staticmethod
    def get_all_logs(
        db: Session,
        current_user
    ):

        if current_user.role.value != "admin":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view audit logs"
            )

        return AuditLogRepository.get_all(
            db=db
        )

    @staticmethod
    def get_entity_logs(
        db: Session,
        entity: str,
        entity_id: int,
        current_user
    ):

        if current_user.role.value != "admin":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view audit logs"
            )

        return AuditLogRepository.get_by_entity(
            db=db,
            entity=entity,
            entity_id=entity_id
        )

    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: int,
        current_user
    ):

        if current_user.role.value != "admin":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view audit logs"
            )

        return AuditLogRepository.get_by_user(
            db=db,
            user_id=user_id
        )