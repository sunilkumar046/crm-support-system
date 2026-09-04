from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from app.services.category_service import CategoryService
from app.core.security import get_current_user, require_role
from app.core.enums import UserRole


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN)
    )
):
    return CategoryService.create_category(
        db=db,
        data=data
    )


@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_all_categories(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return CategoryService.get_all_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return CategoryService.get_category(
        db=db,
        category_id=category_id
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN)
    )
):
    return CategoryService.update_category(
        db=db,
        category_id=category_id,
        data=data
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN)
    )
):
    CategoryService.delete_category(
        db=db,
        category_id=category_id
    )

    return None