from dataclasses import dataclass
from pathlib import PurePosixPath

import boto3

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class S3Object:
    bucket: str
    key: str
    content: bytes
    metadata: dict[str, str]


class S3Service:
    def __init__(self, settings: Settings | None = None, client=None):
        self.settings = settings or get_settings()
        self.client = client or boto3.client("s3", region_name=self.settings.aws_region)

    def download(self, bucket: str, key: str) -> S3Object:
        response = self.client.get_object(Bucket=bucket, Key=key)
        return S3Object(
            bucket=bucket,
            key=key,
            content=response["Body"].read(),
            metadata=response.get("Metadata", {}),
        )

    def upload(
        self,
        bucket: str,
        key: str,
        content: bytes,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            Metadata=metadata or {},
        )

    def move(self, bucket: str, source_key: str, destination_key: str) -> None:
        self.client.copy_object(
            Bucket=bucket,
            CopySource={"Bucket": bucket, "Key": source_key},
            Key=destination_key,
            MetadataDirective="COPY",
        )
        self.client.head_object(Bucket=bucket, Key=destination_key)
        self.client.delete_object(Bucket=bucket, Key=source_key)

    @staticmethod
    def destination_key(source_key: str, destination_prefix: str) -> str:
        path = PurePosixPath(source_key)
        parts = list(path.parts)
        if parts:
            parts[0] = destination_prefix.strip("/")
        return str(PurePosixPath(*parts))

