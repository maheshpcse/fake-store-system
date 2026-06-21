from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.auth.schema import AuthResponse, SignupRequest, UserResponse


USER_COLUMNS = """
    id, email, username, first_name, last_name, phone, street,
    street_number, city, zipcode, is_active, created_at
"""


class AuthService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def login(self, email: str, password: str) -> AuthResponse:
        record = self.db.execute(
            text(f"SELECT {USER_COLUMNS}, password_hash FROM users WHERE email = :email"),
            {"email": email},
        ).mappings().first()
        if record is None or not verify_password(password, record["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not record["is_active"]:
            raise HTTPException(status_code=403, detail="User account is inactive")
        return self._issue_session(dict(record))

    def signup(self, payload: SignupRequest) -> AuthResponse:
        duplicate = self.db.execute(
            text(
                """
                SELECT email, username
                FROM users
                WHERE email = :email OR username = :username
                LIMIT 1
                """
            ),
            {"email": payload.email, "username": payload.username},
        ).mappings().first()
        if duplicate:
            field = "email" if duplicate["email"] == payload.email else "username"
            raise HTTPException(status_code=409, detail=f"{field.capitalize()} already exists")

        next_id = self.db.scalar(text("SELECT COALESCE(MAX(id), 0) + 1 FROM users"))
        try:
            self.db.execute(
                text(
                    """
                    INSERT INTO users (
                        id, email, username, password_hash, first_name,
                        last_name, is_active
                    ) VALUES (
                        :id, :email, :username, :password_hash, :first_name,
                        :last_name, TRUE
                    )
                    """
                ),
                {
                    "id": next_id,
                    "email": payload.email,
                    "username": payload.username,
                    "password_hash": hash_password(payload.password),
                    "first_name": payload.first_name.strip(),
                    "last_name": payload.last_name.strip(),
                },
            )
            customer_role_id = self.db.scalar(
                text("SELECT id FROM roles WHERE name = 'customer' LIMIT 1")
            )
            if customer_role_id:
                self.db.execute(
                    text(
                        "INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"
                    ),
                    {"user_id": next_id, "role_id": customer_role_id},
                )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="Email or username already exists") from exc

        user = self._get_user(next_id)
        return self._issue_session(user)

    def refresh(self, refresh_token: str) -> AuthResponse:
        payload = decode_token(refresh_token, "refresh", self.settings)
        token_digest = hash_token(refresh_token)
        stored = self.db.execute(
            text(
                """
                SELECT id, user_id, expires_at, revoked_at
                FROM refresh_tokens
                WHERE token_hash = :token_hash
                """
            ),
            {"token_hash": token_digest},
        ).mappings().first()
        if stored is None or stored["revoked_at"] is not None:
            raise HTTPException(status_code=401, detail="Refresh token is invalid or revoked")
        expires_at = stored["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        if int(payload["sub"]) != stored["user_id"]:
            raise HTTPException(status_code=401, detail="Refresh token user mismatch")

        self.db.execute(
            text("UPDATE refresh_tokens SET revoked_at = CURRENT_TIMESTAMP WHERE id = :id"),
            {"id": stored["id"]},
        )
        user = self._get_user(stored["user_id"])
        return self._issue_session(user, commit=True)

    def logout(self, refresh_token: str | None) -> None:
        if refresh_token:
            self.db.execute(
                text(
                    """
                    UPDATE refresh_tokens
                    SET revoked_at = CURRENT_TIMESTAMP
                    WHERE token_hash = :token_hash AND revoked_at IS NULL
                    """
                ),
                {"token_hash": hash_token(refresh_token)},
            )
            self.db.commit()

    def _issue_session(
        self,
        user: dict[str, Any],
        *,
        commit: bool = True,
    ) -> AuthResponse:
        access_token, _ = create_token(
            user["id"],
            "access",
            timedelta(minutes=self.settings.access_token_expire_minutes),
            self.settings,
        )
        refresh_token, refresh_expires_at = create_token(
            user["id"],
            "refresh",
            timedelta(days=self.settings.refresh_token_expire_days),
            self.settings,
        )
        self.db.execute(
            text(
                """
                INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
                VALUES (:user_id, :token_hash, :expires_at)
                """
            ),
            {
                "user_id": user["id"],
                "token_hash": hash_token(refresh_token),
                "expires_at": refresh_expires_at.replace(tzinfo=None),
            },
        )
        if commit:
            self.db.commit()
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    def _get_user(self, user_id: int) -> dict[str, Any]:
        user = self.db.execute(
            text(f"SELECT {USER_COLUMNS} FROM users WHERE id = :user_id"),
            {"user_id": user_id},
        ).mappings().first()
        if user is None or not user["is_active"]:
            raise HTTPException(status_code=401, detail="User is inactive or no longer exists")
        return dict(user)
