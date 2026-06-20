from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.modules.payments.model import BatchStatus


class BatchSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    s3_bucket: str
    s3_key: str
    checksum: str
    status: BatchStatus
    total_rows: int
    valid_rows: int
    invalid_rows: int
    total_amount: Decimal
    success_count: int
    failed_count: int
    pending_count: int
    refunded_count: int
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None


class StageError(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_row_number: int
    transaction_id: str | None
    error_reason: str | None

