import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["PAYMENT_AMOUNT_MUST_MATCH_ORDER"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.payments.model import Order, User


@pytest.fixture
def db() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        session.add_all(
            [
                User(id=6, email="user6@example.com"),
                User(id=7, email="user7@example.com"),
                User(id=8, email="user8@example.com"),
                Order(id=6, user_id=6, final_amount=150.75, currency="USD"),
                Order(id=7, user_id=7, final_amount=89.99, currency="USD"),
                Order(id=8, user_id=8, final_amount=20.00, currency="USD"),
            ]
        )
        session.commit()
        yield session

