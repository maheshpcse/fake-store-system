from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.modules.auth.schema import SignupRequest
from app.modules.auth.service import AuthService


def auth_db() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(40),
                    street VARCHAR(255),
                    street_number VARCHAR(30),
                    city VARCHAR(100),
                    zipcode VARCHAR(30),
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE roles (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, role_id)
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE refresh_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash CHAR(64) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    revoked_at DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        connection.execute(text("INSERT INTO roles (id, name) VALUES (1, 'customer')"))
    return Session(engine, expire_on_commit=False)


def test_signup_login_refresh_and_logout() -> None:
    db = auth_db()
    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        jwt_secret_key="test-secret-that-is-long-enough",
        access_token_expire_minutes=10,
        refresh_token_expire_days=1,
    )
    service = AuthService(db, settings)

    signup = service.signup(
        SignupRequest(
            first_name="Store",
            last_name="User",
            username="store_user",
            email="store@example.com",
            password="password123",
        )
    )
    assert signup.user.email == "store@example.com"
    assert signup.access_token
    assert signup.refresh_token

    login = service.login("store@example.com", "password123")
    assert login.user.id == signup.user.id

    refreshed = service.refresh(login.refresh_token)
    assert refreshed.access_token != login.access_token
    assert refreshed.refresh_token != login.refresh_token

    service.logout(refreshed.refresh_token)
    revoked_at = db.scalar(
        text(
            """
            SELECT revoked_at FROM refresh_tokens
            WHERE token_hash IS NOT NULL
            ORDER BY id DESC LIMIT 1
            """
        )
    )
    assert revoked_at is not None
    db.close()
