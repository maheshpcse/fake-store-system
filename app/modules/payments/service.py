import hashlib
import math
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.modules.payments.model import (
    BatchStatus,
    FileProcessingLog,
    FileStatus,
    Payment,
    PaymentReportBatch,
    PaymentReportStage,
)
from app.modules.payments.repository import PaymentReportRepository
from app.services.data_processing.processors import (
    PaymentReportProcessorFactory,
    UnsupportedFileTypeError,
    normalize_payment_frame,
)


ALLOWED_METHODS = {"credit_card", "debit_card", "upi", "net_banking", "paypal", "cash"}
ALLOWED_STATUSES = {"success", "failed", "pending", "refunded"}
CARD_METHODS = {"credit_card", "debit_card"}


class PaymentReportService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.repository = PaymentReportRepository(db)

    def process(
        self,
        *,
        file_name: str,
        content: bytes,
        s3_bucket: str,
        s3_key: str,
        lambda_request_id: str | None = None,
    ) -> tuple[PaymentReportBatch, bool]:
        checksum = hashlib.sha256(content).hexdigest()
        existing = self.repository.get_batch_by_checksum(checksum)
        if existing and existing.status in {
            BatchStatus.COMPLETED,
            BatchStatus.PARTIALLY_COMPLETED,
        }:
            return existing, False

        batch = existing or self.repository.create_batch(
            file_name=file_name,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            checksum=checksum,
            status=BatchStatus.PROCESSING,
        )
        log = self.repository.create_log(
            batch_id=batch.id,
            file_name=file_name,
            source="S3",
            status=FileStatus.PROCESSING,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            checksum=checksum,
            file_size=len(content),
            lambda_request_id=lambda_request_id,
        )
        self.db.commit()

        try:
            processor = PaymentReportProcessorFactory.create(file_name)
            frame = normalize_payment_frame(processor.read(content))
            self._stage(batch, frame)
            self._validate_and_promote(batch, log)
            return batch, True
        except UnsupportedFileTypeError as exc:
            self._fail(batch, log, FileStatus.UNSUPPORTED_FILE_TYPE, str(exc))
            raise
        except ValueError as exc:
            self._fail(batch, log, FileStatus.INVALID_FILE_STRUCTURE, str(exc))
            raise
        except Exception as exc:
            self.db.rollback()
            self._fail(batch, log, FileStatus.DATABASE_FAILED, str(exc))
            raise

    def _stage(self, batch: PaymentReportBatch, frame: pd.DataFrame) -> None:
        rows: list[PaymentReportStage] = []
        for record in frame.to_dict(orient="records"):
            rows.append(
                PaymentReportStage(
                    batch_id=batch.id,
                    source_row_number=int(record["source_row_number"]),
                    transaction_id=self._optional_string(record.get("transaction_id")),
                    order_id=self._optional_int(record.get("order_id")),
                    user_id=self._optional_int(record.get("user_id")),
                    method=self._optional_string(record.get("method")),
                    card_last4=self._optional_string(record.get("card_last4")),
                    amount=self._optional_decimal(record.get("amount")),
                    currency=self._optional_string(record.get("currency")),
                    status=self._optional_string(record.get("status")),
                    paid_at=self._optional_datetime(record.get("paid_at")),
                    raw_data=self._json_safe(record),
                )
            )
        self.repository.add_stage_rows(rows)
        batch.total_rows = len(rows)
        batch.status = BatchStatus.STAGED
        self.db.commit()

    def _validate_and_promote(
        self, batch: PaymentReportBatch, log: FileProcessingLog
    ) -> None:
        batch.status = BatchStatus.VALIDATING
        log.status = FileStatus.VALIDATING
        self.db.commit()

        rows = self.repository.get_stage_rows(batch.id)
        order_ids = {row.order_id for row in rows if row.order_id is not None}
        transaction_ids = {
            row.transaction_id for row in rows if row.transaction_id is not None
        }
        orders = self.repository.get_orders(order_ids)
        existing_transactions = self.repository.existing_transaction_ids(transaction_ids)
        duplicate_transactions = {
            value
            for value in transaction_ids
            if sum(row.transaction_id == value for row in rows) > 1
        }

        valid_rows: list[PaymentReportStage] = []
        for row in rows:
            errors: list[str] = []
            order = orders.get(row.order_id) if row.order_id else None

            if not row.transaction_id:
                errors.append("transaction_id is required")
            elif row.transaction_id in duplicate_transactions:
                errors.append("duplicate transaction_id in file")
            elif row.transaction_id in existing_transactions:
                errors.append("transaction_id already exists")
            if row.order_id is None or row.order_id <= 0:
                errors.append("order_id must be a positive integer")
            elif order is None:
                errors.append("order does not exist")
            if row.user_id is None or row.user_id <= 0:
                errors.append("user_id must be a positive integer")
            elif order and order.user_id != row.user_id:
                errors.append("order does not belong to user")
            if row.amount is None or row.amount <= 0:
                errors.append("amount must be greater than zero")
            elif (
                order
                and self.settings.payment_amount_must_match_order
                and row.amount != order.final_amount
            ):
                errors.append("amount does not match order final_amount")
            if row.currency not in self.settings.supported_currencies:
                errors.append("unsupported currency")
            if row.method not in ALLOWED_METHODS:
                errors.append("unsupported payment method")
            if row.status not in ALLOWED_STATUSES:
                errors.append("unsupported payment status")
            if row.method in CARD_METHODS and (
                not row.card_last4
                or len(row.card_last4) != 4
                or not row.card_last4.isdigit()
            ):
                errors.append("card_last4 must contain four digits")
            if row.status == "success" and row.paid_at is None:
                errors.append("paid_at is required for successful payments")

            row.is_valid = not errors
            row.error_reason = "; ".join(errors) or None
            if row.is_valid:
                valid_rows.append(row)

        payments = [
            Payment(
                order_id=row.order_id,
                user_id=row.user_id,
                method=row.method,
                card_last4=row.card_last4,
                amount=row.amount,
                currency=row.currency,
                status=row.status,
                transaction_id=row.transaction_id,
                paid_at=row.paid_at,
                batch_id=batch.id,
                source_stage_id=row.id,
            )
            for row in valid_rows
        ]
        self.repository.add_payments(payments)
        self._finish_batch(batch, log, rows, valid_rows)
        self.db.commit()

    def _finish_batch(
        self,
        batch: PaymentReportBatch,
        log: FileProcessingLog,
        rows: list[PaymentReportStage],
        valid_rows: list[PaymentReportStage],
    ) -> None:
        invalid_count = len(rows) - len(valid_rows)
        status_counts = {
            status: sum(row.status == status for row in valid_rows)
            for status in ALLOWED_STATUSES
        }
        batch.valid_rows = len(valid_rows)
        batch.invalid_rows = invalid_count
        batch.total_amount = sum(
            (row.amount or Decimal("0") for row in valid_rows), Decimal("0")
        )
        batch.success_count = status_counts["success"]
        batch.failed_count = status_counts["failed"]
        batch.pending_count = status_counts["pending"]
        batch.refunded_count = status_counts["refunded"]
        batch.completed_at = datetime.now(timezone.utc)

        if not rows or not valid_rows:
            batch.status = BatchStatus.FAILED
            log.status = FileStatus.FAILED
        elif invalid_count:
            batch.status = BatchStatus.PARTIALLY_COMPLETED
            log.status = FileStatus.PARTIALLY_COMPLETED
        else:
            batch.status = BatchStatus.COMPLETED
            log.status = FileStatus.COMPLETED

        log.total_rows = len(rows)
        log.valid_rows = len(valid_rows)
        log.invalid_rows = invalid_count
        log.completed_at = batch.completed_at

    def _fail(
        self,
        batch: PaymentReportBatch,
        log: FileProcessingLog,
        status: FileStatus,
        message: str,
    ) -> None:
        batch.status = BatchStatus.FAILED
        batch.error_message = message[:4000]
        batch.completed_at = datetime.now(timezone.utc)
        log.status = status
        log.error_message = message[:4000]
        log.completed_at = batch.completed_at
        self.db.commit()

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        try:
            if value is None or pd.isna(value):
                return None
            number = float(value)
            return int(number) if number.is_integer() else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _optional_decimal(value: Any) -> Decimal | None:
        try:
            if value is None or pd.isna(value):
                return None
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _optional_datetime(value: Any) -> datetime | None:
        if value is None or pd.isna(value):
            return None
        if hasattr(value, "to_pydatetime"):
            return value.to_pydatetime()
        return value if isinstance(value, datetime) else None

    @staticmethod
    def _json_safe(record: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in record.items():
            if value is None or pd.isna(value):
                result[key] = None
            elif hasattr(value, "isoformat"):
                result[key] = value.isoformat()
            elif hasattr(value, "item"):
                result[key] = value.item()
            else:
                result[key] = value
        return result

