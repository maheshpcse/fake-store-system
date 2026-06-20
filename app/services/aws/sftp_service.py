import io
from dataclasses import dataclass
from pathlib import PurePosixPath

import paramiko

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class RemoteFile:
    path: str
    name: str
    size: int


class SFTPService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.transport: paramiko.Transport | None = None
        self.client: paramiko.SFTPClient | None = None

    def __enter__(self) -> "SFTPService":
        self.transport = paramiko.Transport((self.settings.sftp_host, self.settings.sftp_port))
        self.transport.connect(
            username=self.settings.sftp_username,
            password=self.settings.sftp_password,
        )
        self.client = paramiko.SFTPClient.from_transport(self.transport)
        return self

    def __exit__(self, *_: object) -> None:
        if self.client:
            self.client.close()
        if self.transport:
            self.transport.close()

    def list_payment_files(self) -> list[RemoteFile]:
        assert self.client is not None
        supported = {".csv", ".xlsx", ".json"}
        files: list[RemoteFile] = []
        for item in self.client.listdir_attr(self.settings.sftp_inbound_path):
            path = str(PurePosixPath(self.settings.sftp_inbound_path, item.filename))
            if PurePosixPath(item.filename).suffix.lower() in supported:
                files.append(RemoteFile(path=path, name=item.filename, size=item.st_size))
        return files

    def download(self, remote_path: str) -> bytes:
        assert self.client is not None
        buffer = io.BytesIO()
        self.client.getfo(remote_path, buffer)
        return buffer.getvalue()

    def archive(self, remote_path: str) -> None:
        assert self.client is not None
        destination = str(
            PurePosixPath(self.settings.sftp_archive_path, PurePosixPath(remote_path).name)
        )
        self.client.rename(remote_path, destination)

