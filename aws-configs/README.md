# AWS console configuration templates

These files describe the AWS resources needed by the Fake Store payment-file
pipeline. Replace every `${PLACEHOLDER}` before using a configuration.

## Recommended creation order

1. `vpc/vpc-and-security-groups.json`
2. `rds/mysql.json` if MySQL is hosted in Amazon RDS
3. `s3/bucket.json`
4. `secrets-manager/secrets.json`
5. `ssm/parameters.json`
6. `sqs/dead-letter-queue.json`
7. IAM trust and permissions files under `iam/`
8. The two Lambda configurations under `lambda/`
9. `s3/event-notification.json`
10. `eventbridge/sftp-schedule.json`
11. CloudWatch log retention and alarms under `cloudwatch/`

## AWS console locations

| Service | Console path | Configuration file |
| --- | --- | --- |
| VPC | VPC → Your VPCs, Subnets, Security groups, Endpoints | `vpc/vpc-and-security-groups.json` |
| RDS | RDS → Databases → Create database | `rds/mysql.json` |
| S3 | S3 → Create bucket → Properties/Management | `s3/bucket.json` |
| Secrets Manager | Secrets Manager → Store a new secret | `secrets-manager/secrets.json` |
| Parameter Store | Systems Manager → Parameter Store → Create parameter | `ssm/parameters.json` |
| SQS | SQS → Create queue | `sqs/dead-letter-queue.json` |
| IAM Lambda roles | IAM → Roles → Create role → Lambda | `iam/lambda-trust-policy.json` and the matching permissions file |
| IAM Scheduler role | IAM → Roles → Create role → Custom trust policy | `iam/eventbridge-scheduler-*.json` |
| Lambda | Lambda → Create function → Author from scratch | `lambda/*.json` |
| S3 trigger | Lambda → Processor function → Add trigger → S3 | `s3/event-notification.json` |
| Lambda resource policy | Lambda → Processor → Configuration → Permissions | `iam/s3-invoke-lambda-permission.json` |
| Scheduler | EventBridge → Scheduler → Schedules → Create schedule | `eventbridge/sftp-schedule.json` |
| CloudWatch Logs | CloudWatch → Log groups | `cloudwatch/log-groups.json` |
| SNS alerts | SNS → Topics → Create topic | `sns/alerts-topic.json` |
| CloudWatch alarms | CloudWatch → Alarms → Create alarm | `cloudwatch/alarms.json` |

## Shared placeholders

| Placeholder | Example |
| --- | --- |
| `${AWS_ACCOUNT_ID}` | `123456789012` |
| `${AWS_REGION}` | `ap-south-1` |
| `${S3_BUCKET_NAME}` | `fake-store-payment-files-123456789012` |
| `${SFTP_LAMBDA_NAME}` | `fake-store-sftp-to-s3` |
| `${PROCESSOR_LAMBDA_NAME}` | `fake-store-payment-processor` |
| `${SFTP_LAMBDA_ROLE_NAME}` | `fake-store-sftp-lambda-role` |
| `${PROCESSOR_LAMBDA_ROLE_NAME}` | `fake-store-processor-lambda-role` |
| `${VPC_ID}` | `vpc-0123456789abcdef0` |
| `${PRIVATE_SUBNET_1}` | `subnet-0123456789abcdef0` |
| `${PRIVATE_SUBNET_2}` | `subnet-0fedcba9876543210` |
| `${LAMBDA_SECURITY_GROUP_ID}` | `sg-0123456789abcdef0` |
| `${RDS_SECURITY_GROUP_ID}` | `sg-0fedcba9876543210` |

## Important console notes

- Use Python 3.12 and `x86_64` for the ZIP files currently in
  `deployment/lambda/dist/`.
- Lambda environment variables have a total 4 KB quota. Do not store database
  or SFTP passwords directly in source-controlled configuration files.
- The code currently reads `DATABASE_URL` and SFTP values from environment
  variables. The Secrets Manager and SSM files are secure target designs; code
  changes are required before replacing those environment variables with secret
  names alone.
- Attach the Lambdas to private subnets only if those subnets have the required
  outbound path to S3 and the external SFTP host, through a NAT gateway or
  suitable VPC endpoints/network route.
- The S3 trigger must use the `raw/` prefix. The processor writes to the same
  bucket, so triggering on the whole bucket would create an invocation loop.

## Lambda ZIP files and handlers

| Function | ZIP | Handler |
| --- | --- | --- |
| SFTP ingestion | `deployment/lambda/dist/fake-store-sftp-to-s3.zip` | `app.workers.lambda_handlers.sftp_to_s3_handler.lambda_handler` |
| Payment processor | `deployment/lambda/dist/fake-store-payment-processor.zip` | `app.workers.lambda_handlers.payment_file_processor_handler.lambda_handler` |

The JSON files are templates for console entry and AWS CLI/API payloads. Some
console screens split one template into multiple panels, especially Lambda and
VPC configuration.
