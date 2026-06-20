from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.payments.repository import PaymentReportRepository
from app.modules.payments.schema import BatchSummary, StageError
from app.modules.payments.service import PaymentReportService

router = APIRouter(prefix="/reports", tags=["payment reports"])


@router.post("/upload", response_model=BatchSummary, status_code=status.HTTP_201_CREATED)
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BatchSummary:
    if Path(file.filename or "").suffix.lower() not in {".csv", ".xlsx", ".json"}:
        raise HTTPException(status_code=415, detail="Supported file types: csv, xlsx, json")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    try:
        batch, _ = PaymentReportService(db).process(
            file_name=file.filename or "payment-report.csv",
            content=content,
            s3_bucket="local",
            s3_key=f"local/{file.filename}",
        )
        return BatchSummary.model_validate(batch)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{batch_id}", response_model=BatchSummary)
def get_report_status(
    batch_id: int,
    db: Session = Depends(get_db),
) -> BatchSummary:
    batch = PaymentReportRepository(db).get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchSummary.model_validate(batch)


@router.get("/{batch_id}/errors", response_model=list[StageError])
def get_report_errors(
    batch_id: int,
    db: Session = Depends(get_db),
) -> list[StageError]:
    repository = PaymentReportRepository(db)
    if repository.get_batch(batch_id) is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return [
        StageError.model_validate(row)
        for row in repository.get_invalid_rows(batch_id)
    ]

