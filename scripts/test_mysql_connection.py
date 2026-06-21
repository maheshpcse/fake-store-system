"""Test the DATABASE_URL from .env without starting the API server."""

import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Allow direct execution with:
# python scripts/test_mysql_connection.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import engine


def main() -> None:
    try:
        with engine.connect() as connection:
            database = connection.scalar(text("SELECT DATABASE()"))
            version = connection.scalar(text("SELECT VERSION()"))
            table_count = connection.scalar(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    """
                )
            )
            print(f"Connected to database: {database}")
            print(f"MySQL version: {version}")
            print(f"Tables found: {table_count}")
    except OperationalError as exc:
        message = str(exc.orig)
        if "getaddrinfo failed" in message:
            raise SystemExit(
                "MySQL host could not be resolved. Check DATABASE_URL in .env. "
                "If the password contains @, encode it as %40. Other reserved "
                "characters must also be URL-encoded."
            ) from None
        raise SystemExit(f"MySQL connection failed: {message}") from None


if __name__ == "__main__":
    main()
