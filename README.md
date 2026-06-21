# Fake Store Payment File Processor

FastAPI and SQLAlchemy implementation of the workflow documented in
[`PAYMENT_FILE_PROCESSING_SAMPLE.md`](PAYMENT_FILE_PROCESSING_SAMPLE.md):

```text
SFTP -> Lambda -> S3 raw -> processor Lambda -> stage -> validation
     -> payments -> S3 archive/error
```

## Included

- MySQL SQLAlchemy models for users, orders, payments, batches, stage rows, and logs
- Alembic migration
- CSV, XLSX, and JSON processor factory
- Row-level validation and persisted error reasons
- File checksum and transaction ID idempotency
- SFTP ingestion and S3 processing Lambda handlers
- FastAPI upload, batch status, and row-error endpoints
- SQLite-backed integration tests

## Local MySQL and frontend setup

SQLyog-ready table and seed scripts are available in
[`MySQL DB schemas/README.md`](MySQL%20DB%20schemas/README.md).

Execute these files in order:

```text
MySQL DB schemas/00_create_database.sql
MySQL DB schemas/01_create_all_tables.sql
MySQL DB schemas/02_seed_all_data.sql
MySQL DB schemas/03_verify_database.sql
```

For a manually created SQLyog database, these scripts are the authoritative
local schema. Do not also run the initial Alembic migration against the same
empty database because both paths create overlapping tables.

Copy the local environment template and provide your MySQL password:

```powershell
Copy-Item '.\MySQL DB schemas\local.env.example' .env
```

Then start the API:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/test_mysql_connection.py
uvicorn app.main:app --reload
```

The API allows local Angular, React, and Vite development origins by default.

Useful frontend routes:

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
PATCH /api/v1/users/{user_id}
GET  /api/v1/users/{user_id}/addresses
POST /api/v1/users/{user_id}/addresses
GET /api/v1/categories
GET /api/v1/products
GET /api/v1/products/{product_id}
GET /api/v1/products/{product_id}/reviews
GET /api/v1/users
GET /api/v1/carts/user/{user_id}
GET /api/v1/wishlists/user/{user_id}
GET /api/v1/orders
GET /api/v1/orders/{order_id}
GET /api/v1/payments
GET /api/v1/coupons/{code}
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Create the database:

```sql
CREATE DATABASE fake_store
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Edit `.env`, then run:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

API documentation is available at `http://127.0.0.1:8000/docs`.

## Local upload

The order and user referenced by the file must already exist.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/reports/upload" `
  -F "file=@sample_files/payment_report_20260620_001.csv"
```

Check a batch and its invalid rows:

```text
GET /api/v1/reports/{batch_id}
GET /api/v1/reports/{batch_id}/errors
```

## Lambda entry points

```text
app.workers.lambda_handlers.sftp_to_s3_handler.lambda_handler
app.workers.lambda_handlers.payment_file_processor_handler.lambda_handler
```

AWS console configuration templates for Lambda, S3, IAM, EventBridge,
Secrets Manager, SSM, SQS, CloudWatch, SNS, VPC, and RDS are documented in
[`aws-configs/README.md`](aws-configs/README.md).

Configure the second handler on S3 `ObjectCreated` events limited to the
`raw/` prefix. The S3 service copies and verifies an archive/error object before
deleting the raw object.

If database processing succeeds but the S3 move fails, replaying the event
detects the file checksum and retries the move without inserting payments again.

## Tests

```powershell
pytest -q
```

The test suite uses SQLite for speed; production uses the `DATABASE_URL` from
`.env`.
