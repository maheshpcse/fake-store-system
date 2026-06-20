"""Create payment file processing tables.

Revision ID: 20260620_0001
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260620_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mongo_id", sa.String(50), unique=True),
        sa.Column("email", sa.String(255), unique=True),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mongo_id", sa.String(50), unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("final_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_table(
        "payment_report_batches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("s3_bucket", sa.String(255), nullable=False),
        sa.Column("s3_key", sa.String(1024), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pending_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("refunded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("checksum", name="uq_payment_report_batches_checksum"),
    )
    op.create_table(
        "payment_report_stage",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "batch_id",
            sa.Integer(),
            sa.ForeignKey("payment_report_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(100)),
        sa.Column("order_id", sa.Integer()),
        sa.Column("user_id", sa.Integer()),
        sa.Column("method", sa.String(50)),
        sa.Column("card_last4", sa.String(4)),
        sa.Column("amount", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3)),
        sa.Column("status", sa.String(30)),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("is_valid", sa.Boolean()),
        sa.Column("error_reason", sa.Text()),
        sa.Column("raw_data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("batch_id", "source_row_number", name="uq_stage_batch_row"),
    )
    op.create_index("ix_stage_batch_valid", "payment_report_stage", ["batch_id", "is_valid"])
    op.create_index("ix_payment_report_stage_batch_id", "payment_report_stage", ["batch_id"])
    op.create_index(
        "ix_payment_report_stage_transaction_id", "payment_report_stage", ["transaction_id"]
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("mongo_id", sa.String(50), unique=True),
        sa.Column("legacy_id", sa.Integer(), unique=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("method", sa.String(50), nullable=False),
        sa.Column("card_last4", sa.String(4)),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("transaction_id", sa.String(100), nullable=False, unique=True),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("payment_report_batches.id")),
        sa.Column(
            "source_stage_id",
            sa.Integer(),
            sa.ForeignKey("payment_report_stage.id"),
            unique=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_transaction_id", "payments", ["transaction_id"])
    op.create_table(
        "file_processing_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("payment_report_batches.id")),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("source", sa.String(30), nullable=False, server_default="SFTP"),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("sftp_path", sa.String(1024)),
        sa.Column("s3_bucket", sa.String(255)),
        sa.Column("s3_key", sa.String(1024)),
        sa.Column("checksum", sa.String(64)),
        sa.Column("file_size", sa.Integer()),
        sa.Column("lambda_request_id", sa.String(100)),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_file_logs_checksum_status", "file_processing_logs", ["checksum", "status"]
    )


def downgrade() -> None:
    op.drop_table("file_processing_logs")
    op.drop_table("payments")
    op.drop_table("payment_report_stage")
    op.drop_table("payment_report_batches")
    op.drop_table("orders")
    op.drop_table("users")

