from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    ChangePassword
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    return AuthService.register(
        db=db,
        data=data
    )


@router.post(
    "/login",
    response_model=Token
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    return AuthService.login(
        db=db,
        data=data
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user


@router.put(
    "/change-password"
)
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return AuthService.change_password(
        db=db,
        user=current_user,
        data=data
    )