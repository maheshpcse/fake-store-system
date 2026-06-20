from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fake Store Payment Processor"
    environment: str = "local"
    database_url: str = "mysql+pymysql://root:password@localhost:3306/fake_store"

    aws_region: str = "ap-south-1"
    s3_bucket_name: str = "fake-store-payment-files"
    s3_raw_prefix: str = "raw"
    s3_archive_prefix: str = "archive"
    s3_error_prefix: str = "error"

    sftp_host: str = ""
    sftp_port: int = 22
    sftp_username: str = ""
    sftp_password: str = ""
    sftp_inbound_path: str = "/inbound"
    sftp_archive_path: str = "/archive"

    supported_currencies: list[str] = ["USD"]
    payment_amount_must_match_order: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("supported_currencies", mode="before")
    @classmethod
    def parse_currencies(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip().upper() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

