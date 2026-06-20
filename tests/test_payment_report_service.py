from sqlalchemy import func, select

from app.modules.payments.model import BatchStatus, Payment, PaymentReportStage
from app.modules.payments.service import PaymentReportService


def test_processes_valid_and_invalid_rows(db) -> None:
    content = b"""transactionId,orderId,userId,method,cardLast4,amount,currency,status,paidAt
TXN200001,6,6,credit_card,1234,150.75,USD,success,2026-06-20T08:30:00Z
TXN200002,7,7,upi,,89.99,USD,pending,
TXN200003,8,8,debit_card,5678,-20.00,USD,success,2026-06-20T09:00:00Z
"""
    batch, processed = PaymentReportService(db).process(
        file_name="payments.csv",
        content=content,
        s3_bucket="test",
        s3_key="raw/2026/06/20/payments.csv",
    )

    assert processed is True
    assert batch.status == BatchStatus.PARTIALLY_COMPLETED
    assert batch.total_rows == 3
    assert batch.valid_rows == 2
    assert batch.invalid_rows == 1
    assert db.scalar(select(func.count(Payment.id))) == 2
    invalid = db.scalar(
        select(PaymentReportStage).where(PaymentReportStage.is_valid.is_(False))
    )
    assert invalid is not None
    assert "amount must be greater than zero" in invalid.error_reason


def test_checksum_makes_completed_file_idempotent(db) -> None:
    content = b"""transactionId,orderId,userId,method,amount,currency,status,paidAt
TXN200010,6,6,upi,150.75,USD,success,2026-06-20T08:30:00Z
"""
    service = PaymentReportService(db)
    first, first_processed = service.process(
        file_name="payments.csv",
        content=content,
        s3_bucket="test",
        s3_key="raw/payments.csv",
    )
    second, second_processed = service.process(
        file_name="renamed.csv",
        content=content,
        s3_bucket="test",
        s3_key="raw/renamed.csv",
    )

    assert first.status == BatchStatus.COMPLETED
    assert first_processed is True
    assert second.id == first.id
    assert second_processed is False
    assert db.scalar(select(func.count(Payment.id))) == 1

