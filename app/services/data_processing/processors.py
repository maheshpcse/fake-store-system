import io
import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class UnsupportedFileTypeError(ValueError):
    pass


class PaymentFileProcessor(ABC):
    @abstractmethod
    def read(self, content: bytes) -> pd.DataFrame:
        raise NotImplementedError


class CSVProcessor(PaymentFileProcessor):
    def read(self, content: bytes) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(content), dtype={"cardLast4": "string"})


class ExcelProcessor(PaymentFileProcessor):
    def read(self, content: bytes) -> pd.DataFrame:
        return pd.read_excel(io.BytesIO(content), dtype={"cardLast4": "string"})


class JSONProcessor(PaymentFileProcessor):
    def read(self, content: bytes) -> pd.DataFrame:
        parsed = json.loads(content.decode("utf-8"))
        if isinstance(parsed, dict):
            parsed = parsed.get("payments", parsed.get("data", [parsed]))
        return pd.DataFrame(parsed)


class PaymentReportProcessorFactory:
    processors = {
        ".csv": CSVProcessor,
        ".xlsx": ExcelProcessor,
        ".json": JSONProcessor,
    }

    @classmethod
    def create(cls, file_name: str) -> PaymentFileProcessor:
        extension = Path(file_name).suffix.lower()
        processor = cls.processors.get(extension)
        if processor is None:
            raise UnsupportedFileTypeError(f"Unsupported file type: {extension or 'none'}")
        return processor()


REQUIRED_COLUMNS = {
    "transaction_id",
    "order_id",
    "user_id",
    "method",
    "amount",
    "currency",
    "status",
}

COLUMN_ALIASES = {
    "transactionid": "transaction_id",
    "transaction_id": "transaction_id",
    "orderid": "order_id",
    "order_id": "order_id",
    "userid": "user_id",
    "user_id": "user_id",
    "cardlast4": "card_last4",
    "card_last4": "card_last4",
    "paidat": "paid_at",
    "paid_at": "paid_at",
}


def normalize_payment_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [
        COLUMN_ALIASES.get(
            str(column).strip().replace(" ", "_").replace("-", "_").lower(),
            str(column).strip().replace(" ", "_").replace("-", "_").lower(),
        )
        for column in normalized.columns
    ]
    missing = REQUIRED_COLUMNS.difference(normalized.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    if "card_last4" not in normalized:
        normalized["card_last4"] = None
    if "paid_at" not in normalized:
        normalized["paid_at"] = None

    for column in ("transaction_id", "method", "currency", "status", "card_last4"):
        normalized[column] = normalized[column].map(
            lambda value: None if pd.isna(value) else str(value).strip()
        )

    normalized["method"] = normalized["method"].str.lower()
    normalized["currency"] = normalized["currency"].str.upper()
    normalized["status"] = normalized["status"].str.lower()
    normalized["amount"] = pd.to_numeric(normalized["amount"], errors="coerce")
    normalized["order_id"] = pd.to_numeric(normalized["order_id"], errors="coerce")
    normalized["user_id"] = pd.to_numeric(normalized["user_id"], errors="coerce")
    normalized["paid_at"] = pd.to_datetime(normalized["paid_at"], errors="coerce", utc=True)
    normalized.insert(0, "source_row_number", range(2, len(normalized) + 2))
    return normalized

