from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.customer import Customer
from app.schemas.auth import UserRegister, UserLogin, ChangePassword


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )

    @staticmethod
    def create_access_token(user_id: int) -> str:

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": str(user_id),
            "exp": expire
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    @staticmethod
    def register(
        db: Session,
        data: UserRegister
    ):

        existing_user = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=AuthService.hash_password(
                data.password
            ),
            role=data.role,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        if user.role.value == "customer":
            customer = Customer(
                user_id=user.id,
                status="active"
            )

            db.add(customer)
            db.commit()

        return user

    @staticmethod
    def login(
        db: Session,
        data: UserLogin
    ):

        user = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not AuthService.verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        access_token = AuthService.create_access_token(
            user.id
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        data: ChangePassword
    ):

        if not AuthService.verify_password(
            data.current_password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.password_hash = AuthService.hash_password(
            data.new_password
        )

        db.commit()
        db.refresh(user)

        return {
            "message": "Password changed successfully"
        }