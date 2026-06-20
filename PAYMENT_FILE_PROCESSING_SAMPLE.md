# Payment Report File Processing Sample

This document describes the end-to-end payment report workflow:

```text
SFTP
  -> SFTP-to-S3 Lambda
  -> S3 raw folder
  -> Payment processor Lambda
  -> payment_report_stage
  -> validation
  -> payments
  -> S3 archive or error folder
```

## 1. Expected input file

Example file name:

```text
payment_report_20260620_001.csv
```

Example CSV:

```csv
transactionId,orderId,userId,method,cardLast4,amount,currency,status,paidAt
TXN100006,6,2,credit_card,1234,150.75,USD,success,2026-06-20T08:30:00Z
TXN100007,7,4,upi,,89.99,USD,pending,
TXN100008,8,5,debit_card,5678,-20.00,USD,success,2026-06-20T09:00:00Z
```

Recommended required columns:

- `transactionId`
- `orderId`
- `userId`
- `method`
- `amount`
- `currency`
- `status`

Optional columns:

- `cardLast4`
- `paidAt`

## 2. Suggested S3 folder structure

```text
fake-store-payment-files/
├── raw/2026/06/20/payment_report_20260620_001.csv
├── archive/2026/06/20/payment_report_20260620_001.csv
└── error/2026/06/20/payment_report_20260620_001.csv
```

The `raw` folder receives new files. A successfully processed file is copied to
`archive`; a file that cannot be processed is copied to `error`.

## 3. Step-by-step processing timeline

### Step 1: Find new files on SFTP

The scheduled `sftp_to_s3_handler` Lambda:

1. Reads SFTP credentials from AWS Secrets Manager or environment variables.
2. Connects to SFTP using Paramiko.
3. Lists files from the configured inbound folder.
4. Accepts supported extensions such as `.csv`, `.xlsx`, and `.json`.
5. Ignores files already recorded as completed in `file_processing_logs`.
6. Optionally checks that the file size has stopped changing before downloading.

### Step 2: Register the file

Before uploading, insert a row into `file_processing_logs`.

Suggested values:

```text
file_name       = payment_report_20260620_001.csv
source          = SFTP
status          = DISCOVERED
sftp_path       = /inbound/payment_report_20260620_001.csv
started_at      = current UTC time
```

Use a unique key based on `file_name`, file size, and checksum to prevent the
same file from being processed twice.

### Step 3: Upload to the S3 raw folder

The SFTP Lambda:

1. Downloads the file to Lambda temporary storage.
2. Calculates a SHA-256 checksum.
3. Uploads it to the date-based S3 `raw` key.
4. Adds S3 metadata such as checksum, source file name, and upload time.
5. Updates `file_processing_logs` to `UPLOADED`.
6. Moves the original SFTP file to its SFTP archive folder.

Example S3 key:

```text
raw/2026/06/20/payment_report_20260620_001.csv
```

If the upload fails, update the log to `SFTP_UPLOAD_FAILED`. Do not move the
source file to the SFTP archive folder.

### Step 4: Trigger the processor Lambda

Configure an S3 `ObjectCreated` event for the `raw/` prefix. The event invokes
`payment_file_processor_handler`.

The processor must first:

1. Decode the bucket name and object key from the S3 event.
2. Ignore keys outside the `raw/` folder.
3. Read the object metadata and checksum.
4. Confirm that this exact file has not already completed processing.

S3 events may be delivered more than once, so this idempotency check is
required.

### Step 5: Create a processing batch

Insert one row into `payment_report_batches`.

Example:

```text
file_name       = payment_report_20260620_001.csv
s3_bucket       = fake-store-payment-files
s3_key          = raw/2026/06/20/payment_report_20260620_001.csv
checksum        = <SHA-256 value>
status          = PROCESSING
total_rows      = 0
valid_rows      = 0
invalid_rows    = 0
started_at      = current UTC time
```

The generated batch ID must be attached to every stage row.

### Step 6: Read and normalize the file

Use `PaymentReportProcessorFactory` to choose the processor:

```text
.csv  -> CSVProcessor
.xlsx -> ExcelProcessor
.json -> JSONProcessor
```

Use pandas to:

1. Trim column names and string values.
2. Rename external columns to the application's standard names.
3. Convert camelCase names to normalized fields:

```text
transactionId -> transaction_id
orderId       -> order_id
userId        -> user_id
cardLast4     -> card_last4
paidAt        -> paid_at
```

4. Convert `amount` to a decimal-compatible numeric value.
5. Convert `paid_at` to UTC datetime.
6. Convert `currency`, `method`, and `status` to lowercase or another agreed
   canonical format.
7. Add `source_row_number` so errors can be traced to the original file.

Do not use floating-point values for final database money calculations. Store
amounts using MySQL `DECIMAL`, for example `DECIMAL(12, 2)`.

### Step 7: Load all rows into the stage table

Insert every parsed row into `payment_report_stage`, including rows that may
later fail business validation.

Suggested stage fields:

```text
id
batch_id
source_row_number
transaction_id
order_id
user_id
method
card_last4
amount
currency
status
paid_at
is_valid
error_reason
raw_data
created_at
```

Initially set:

```text
is_valid    = NULL
error_reason = NULL
```

Keeping invalid rows in stage gives support teams a clear audit trail.

### Step 8: Validate stage records

Run row-level validations:

- Required columns are present.
- `transaction_id` is not empty.
- `order_id` and `user_id` contain valid positive IDs.
- The referenced order exists.
- The order belongs to the supplied user.
- `amount` is greater than zero.
- `amount` agrees with `orders.final_amount`, when that is a business rule.
- `currency` is supported, such as `USD`.
- `method` is an allowed value.
- `status` is one of `success`, `failed`, `pending`, or `refunded`.
- `card_last4` contains four digits when a card method is used.
- `paid_at` is present for a successful payment.
- `transaction_id` is not duplicated within the file.
- `transaction_id` does not already exist in `payments`.

For the sample CSV:

```text
row 2: valid
row 3: valid if order 7 and user 4 exist
row 4: invalid because amount is negative
```

For a failed row, set:

```text
is_valid     = FALSE
error_reason = "amount must be greater than zero"
```

For a passed row, set:

```text
is_valid     = TRUE
error_reason = NULL
```

### Step 9: Move valid records to `payments`

Within a database transaction:

1. Select valid stage rows for the batch.
2. Insert new payment records or update permitted existing records.
3. Keep `transaction_id` unique in `payments`.
4. Record `batch_id` or `source_stage_id` in `payments` for traceability.
5. Commit only after all valid rows have been handled.

Recommended duplicate behavior:

- Same `transaction_id` and same values: skip as an idempotent duplicate.
- Same `transaction_id` with different values: reject and record a conflict.
- New `transaction_id`: insert into `payments`.

Invalid records remain in `payment_report_stage` with their error reasons.

### Step 10: Calculate and store the batch summary

Use pandas or SQL aggregation to calculate:

```text
total_rows
valid_rows
invalid_rows
total_amount
success_count
failed_count
pending_count
refunded_count
```

Set the final batch status:

```text
COMPLETED          -> every row is valid
PARTIALLY_COMPLETED -> valid and invalid rows both exist
FAILED             -> no usable rows or a fatal processing error occurred
```

Also update `file_processing_logs` with the batch ID, final status, counts,
completion time, and any fatal error message.

### Step 11: Archive or quarantine the S3 object

For `COMPLETED` or `PARTIALLY_COMPLETED`:

1. Copy the object from `raw/...` to the matching `archive/...` key.
2. Verify that the copied object exists.
3. Delete the original object from `raw/...`.

For `FAILED`:

1. Copy the object from `raw/...` to the matching `error/...` key.
2. Add metadata or tags containing the batch ID and failure category.
3. Verify the copied object.
4. Delete the original object from `raw/...`.

Example final key:

```text
archive/2026/06/20/payment_report_20260620_001.csv
```

## 4. Status flow

```text
DISCOVERED
  -> UPLOADED
  -> PROCESSING
  -> STAGED
  -> VALIDATING
  -> COMPLETED
     or PARTIALLY_COMPLETED
     or FAILED
```

Failure statuses can be more specific:

```text
SFTP_CONNECTION_FAILED
SFTP_DOWNLOAD_FAILED
S3_UPLOAD_FAILED
UNSUPPORTED_FILE_TYPE
INVALID_FILE_STRUCTURE
DATABASE_FAILED
ARCHIVE_FAILED
```

## 5. Transaction boundaries

Use short database transactions:

1. Create the batch and commit.
2. Insert stage rows in chunks and commit.
3. Validate stage rows and commit.
4. Insert valid payments and update batch totals in one transaction.
5. Move the S3 object only after the database transaction succeeds.

Do not keep a database transaction open while downloading or copying an S3
object.

## 6. Retry and idempotency rules

- Use the file checksum as the primary file-level idempotency key.
- Add a unique constraint on `payment_report_batches.checksum`.
- Add a unique constraint on `payments.transaction_id`.
- Make each Lambda safe to retry after a timeout.
- If the database succeeds but S3 archival fails, retry only the archival step.
- Send repeatedly failing S3 events to a dead-letter queue.
- Store the Lambda request ID in `file_processing_logs` for troubleshooting.

## 7. Minimum table relationships

```text
payment_report_batches 1 ─── many payment_report_stage
payment_report_batches 1 ─── many file_processing_logs
payment_report_batches 1 ─── many payments
orders                 1 ─── many payments
users                  1 ─── many payments
```

The stage table is temporary in purpose, but it should not be a MySQL
`TEMPORARY TABLE`. Use a normal persisted table so processing remains
recoverable across Lambda invocations and failures. Old stage rows can be
removed later using a retention job.

## 8. Local test sequence

1. Place the sample CSV in a local test input folder.
2. Invoke the SFTP-to-S3 handler with mocked SFTP and LocalStack/MinIO, or upload
   the file directly to the test S3 `raw/` prefix.
3. Pass a saved S3 `ObjectCreated` event to the processor handler.
4. Confirm one `payment_report_batches` row was created.
5. Confirm every input row exists in `payment_report_stage`.
6. Confirm only valid rows were inserted into `payments`.
7. Confirm invalid rows contain useful `error_reason` values.
8. Confirm the batch counts and totals are correct.
9. Confirm the source object moved from `raw/` to `archive/` or `error/`.
10. Send the same event again and confirm that no duplicate payments are
    created.
