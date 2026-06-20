import enum
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BatchStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    STAGED = "STAGED"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    FAILED = "FAILED"


class FileStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    STAGED = "STAGED"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    FAILED = "FAILED"
    SFTP_CONNECTION_FAILED = "SFTP_CONNECTION_FAILED"
    SFTP_DOWNLOAD_FAILED = "SFTP_DOWNLOAD_FAILED"
    S3_UPLOAD_FAILED = "S3_UPLOAD_FAILED"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    INVALID_FILE_STRUCTURE = "INVALID_FILE_STRUCTURE"
    DATABASE_FAILED = "DATABASE_FAILED"
    ARCHIVE_FAILED = "ARCHIVE_FAILED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mongo_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mongo_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")


class PaymentReportBatch(Base):
    __tablename__ = "payment_report_batches"
    __table_args__ = (UniqueConstraint("checksum", name="uq_payment_report_batches_checksum"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255))
    s3_bucket: Mapped[str] = mapped_column(String(255))
    s3_key: Mapped[str] = mapped_column(String(1024))
    checksum: Mapped[str] = mapped_column(String(64))
    status: Mapped[BatchStatus] = mapped_column(
        Enum(BatchStatus, native_enum=False), default=BatchStatus.PROCESSING
    )
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    pending_count: Mapped[int] = mapped_column(Integer, default=0)
    refunded_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    stage_rows: Mapped[list["PaymentReportStage"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class PaymentReportStage(Base):
    __tablename__ = "payment_report_stage"
    __table_args__ = (
        UniqueConstraint("batch_id", "source_row_number", name="uq_stage_batch_row"),
        Index("ix_stage_batch_valid", "batch_id", "is_valid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("payment_report_batches.id", ondelete="CASCADE"), index=True
    )
    source_row_number: Mapped[int] = mapped_column(Integer)
    transaction_id: Mapped[str | None] = mapped_column(String(100), index=True)
    order_id: Mapped[int | None] = mapped_column(Integer)
    user_id: Mapped[int | None] = mapped_column(Integer)
    method: Mapped[str | None] = mapped_column(String(50))
    card_last4: Mapped[str | None] = mapped_column(String(4))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[str | None] = mapped_column(String(30))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_valid: Mapped[bool | None] = mapped_column(Boolean)
    error_reason: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    batch: Mapped[PaymentReportBatch] = relationship(back_populates="stage_rows")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mongo_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    method: Mapped[str] = mapped_column(String(50))
    card_last4: Mapped[str | None] = mapped_column(String(4))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(30))
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("payment_report_batches.id"))
    source_stage_id: Mapped[int | None] = mapped_column(
        ForeignKey("payment_report_stage.id"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FileProcessingLog(Base):
    __tablename__ = "file_processing_logs"
    __table_args__ = (Index("ix_file_logs_checksum_status", "checksum", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("payment_report_batches.id"))
    file_name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(30), default="SFTP")
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus, native_enum=False))
    sftp_path: Mapped[str | None] = mapped_column(String(1024))
    s3_bucket: Mapped[str | None] = mapped_column(String(255))
    s3_key: Mapped[str | None] = mapped_column(String(1024))
    checksum: Mapped[str | None] = mapped_column(String(64))
    file_size: Mapped[int | None] = mapped_column(Integer)
    lambda_request_id: Mapped[str | None] = mapped_column(String(100))
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

