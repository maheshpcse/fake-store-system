import logging
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import unquote_plus

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.modules.payments.model import BatchStatus
from app.modules.payments.service import PaymentReportService
from app.services.aws.s3_service import S3Service

logger = logging.getLogger(__name__)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    settings = get_settings()
    s3 = S3Service(settings)
    results: list[dict[str, Any]] = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        if not key.startswith(f"{settings.s3_raw_prefix.strip('/')}/"):
            logger.info("Ignoring object outside raw prefix: %s", key)
            continue

        obj = s3.download(bucket, key)
        request_id = getattr(context, "aws_request_id", None)
        db = SessionLocal()
        try:
            batch, processed = PaymentReportService(db, settings).process(
                file_name=PurePosixPath(key).name,
                content=obj.content,
                s3_bucket=bucket,
                s3_key=key,
                lambda_request_id=request_id,
            )
            destination_prefix = (
                settings.s3_error_prefix
                if batch.status == BatchStatus.FAILED
                else settings.s3_archive_prefix
            )
            destination_key = s3.destination_key(key, destination_prefix)
            # If database work succeeded but archival failed, an S3 replay
            # returns processed=False and safely retries only this move.
            s3.move(bucket, key, destination_key)
            results.append(
                {
                    "batch_id": batch.id,
                    "status": batch.status.value,
                    "processed": processed,
                    "destination_key": destination_key,
                }
            )
        except Exception:
            logger.exception("Payment file processing failed for s3://%s/%s", bucket, key)
            error_key = s3.destination_key(key, settings.s3_error_prefix)
            try:
                s3.move(bucket, key, error_key)
            except Exception:
                logger.exception("Could not move failed file to %s", error_key)
            raise
        finally:
            db.close()

    return {"processed_records": len(results), "results": results}


lambda_handler = handler
