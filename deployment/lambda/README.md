# AWS Lambda ZIP deployment

Build both Python 3.12 deployment archives from the project root:

```powershell
.\deployment\lambda\build_lambda_zips.ps1
```

The default architecture is `x86_64`. For Lambda functions configured as
Graviton/ARM64:

```powershell
.\deployment\lambda\build_lambda_zips.ps1 -Architecture arm64
```

Generated files:

```text
deployment/lambda/dist/fake-store-sftp-to-s3.zip
deployment/lambda/dist/fake-store-payment-processor.zip
```

AWS Lambda configuration:

| Function | Runtime | Handler |
| --- | --- | --- |
| SFTP to S3 | Python 3.12 | `app.workers.lambda_handlers.sftp_to_s3_handler.lambda_handler` |
| Payment processor | Python 3.12 | `app.workers.lambda_handlers.payment_file_processor_handler.lambda_handler` |

Set the Lambda architecture to the same value used by the build script.

The archives intentionally do not bundle `boto3`, because it is available in
the AWS Lambda Python runtime.

For the payment processor, configure:

- An S3 `ObjectCreated` trigger filtered to the `raw/` prefix.
- S3 read, write, copy, delete, and head-object permissions.
- Network access to MySQL.
- Environment variables from the project's `.env.example`.

For SFTP ingestion, configure:

- A scheduled EventBridge trigger.
- Network access to the SFTP server and MySQL.
- S3 put-object permission.
- SFTP and database environment variables or secret-resolution integration.

If a ZIP exceeds the AWS console's direct-upload limit, upload it to S3 and
choose **Upload from Amazon S3 location** in the Lambda console.

Service-by-service AWS console templates are available in
[`aws-configs`](../../aws-configs/README.md).
