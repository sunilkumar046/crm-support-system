from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import require_role

from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_all_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return AuditLogService.get_all_logs(
        db=db,
        current_user=current_user
    )


@router.get(
    "/entity/{entity}/{entity_id}",
    response_model=list[AuditLogResponse]
)
def get_entity_audit_logs(
    entity: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return AuditLogService.get_entity_logs(
        db=db,
        entity=entity,
        entity_id=entity_id,
        current_user=current_user
    )


@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse]
)
def get_user_audit_logs(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):

    return AuditLogService.get_user_logs(
        db=db,
        user_id=user_id,
        current_user=current_user
    )