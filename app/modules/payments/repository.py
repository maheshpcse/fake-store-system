from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payments.model import (
    FileProcessingLog,
    Order,
    Payment,
    PaymentReportBatch,
    PaymentReportStage,
)


class PaymentReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_batch(self, batch_id: int) -> PaymentReportBatch | None:
        return self.db.get(PaymentReportBatch, batch_id)

    def get_batch_by_checksum(self, checksum: str) -> PaymentReportBatch | None:
        return self.db.scalar(
            select(PaymentReportBatch).where(PaymentReportBatch.checksum == checksum)
        )

    def create_batch(self, **values: object) -> PaymentReportBatch:
        batch = PaymentReportBatch(**values)
        self.db.add(batch)
        self.db.flush()
        return batch

    def create_log(self, **values: object) -> FileProcessingLog:
        log = FileProcessingLog(**values)
        self.db.add(log)
        self.db.flush()
        return log

    def add_stage_rows(self, rows: Iterable[PaymentReportStage]) -> None:
        self.db.add_all(list(rows))
        self.db.flush()

    def get_stage_rows(self, batch_id: int) -> list[PaymentReportStage]:
        return list(
            self.db.scalars(
                select(PaymentReportStage)
                .where(PaymentReportStage.batch_id == batch_id)
                .order_by(PaymentReportStage.source_row_number)
            )
        )

    def get_invalid_rows(self, batch_id: int) -> list[PaymentReportStage]:
        return list(
            self.db.scalars(
                select(PaymentReportStage).where(
                    PaymentReportStage.batch_id == batch_id,
                    PaymentReportStage.is_valid.is_(False),
                )
            )
        )

    def get_orders(self, order_ids: set[int]) -> dict[int, Order]:
        if not order_ids:
            return {}
        return {
            order.id: order
            for order in self.db.scalars(select(Order).where(Order.id.in_(order_ids)))
        }

    def existing_transaction_ids(self, transaction_ids: set[str]) -> set[str]:
        if not transaction_ids:
            return set()
        return set(
            self.db.scalars(
                select(Payment.transaction_id).where(
                    Payment.transaction_id.in_(transaction_ids)
                )
            )
        )

    def add_payments(self, payments: Iterable[Payment]) -> None:
        self.db.add_all(list(payments))
        self.db.flush()

