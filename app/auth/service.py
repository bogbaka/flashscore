from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(
        self,
        email: str,
        password: str,
    ) -> User:
        existing_user = self.db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing_user is not None:
            raise ValueError(
                "Email already registered"
            )

        user = User(
            email=email,
            password_hash=hash_password(password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login_user(
        self,
        email: str,
        password: str,
    ) -> str | None:
        user = self.db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return create_access_token(user.id)