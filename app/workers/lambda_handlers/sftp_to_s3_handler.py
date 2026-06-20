import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.modules.payments.model import FileProcessingLog, FileStatus
from app.services.aws.s3_service import S3Service
from app.services.aws.sftp_service import SFTPService

logger = logging.getLogger(__name__)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    settings = get_settings()
    s3 = S3Service(settings)
    request_id = getattr(context, "aws_request_id", None)
    uploaded: list[str] = []

    with SFTPService(settings) as sftp:
        for remote_file in sftp.list_payment_files():
            db = SessionLocal()
            log = FileProcessingLog(
                file_name=remote_file.name,
                source="SFTP",
                status=FileStatus.DISCOVERED,
                sftp_path=remote_file.path,
                file_size=remote_file.size,
                lambda_request_id=request_id,
            )
            db.add(log)
            db.commit()
            try:
                content = sftp.download(remote_file.path)
                checksum = hashlib.sha256(content).hexdigest()
                now = datetime.now(timezone.utc)
                key = (
                    f"{settings.s3_raw_prefix.strip('/')}/"
                    f"{now:%Y/%m/%d}/{remote_file.name}"
                )
                s3.upload(
                    settings.s3_bucket_name,
                    key,
                    content,
                    metadata={
                        "checksum": checksum,
                        "source-file-name": remote_file.name,
                        "uploaded-at": now.isoformat(),
                    },
                )
                sftp.archive(remote_file.path)
                log.status = FileStatus.UPLOADED
                log.s3_bucket = settings.s3_bucket_name
                log.s3_key = key
                log.checksum = checksum
                log.completed_at = now
                db.commit()
                uploaded.append(key)
            except Exception as exc:
                db.rollback()
                log = db.merge(log)
                log.status = FileStatus.S3_UPLOAD_FAILED
                log.error_message = str(exc)[:4000]
                log.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.exception("Failed to ingest SFTP file %s", remote_file.path)
            finally:
                db.close()

    return {"uploaded_count": len(uploaded), "keys": uploaded}


lambda_handler = handler

