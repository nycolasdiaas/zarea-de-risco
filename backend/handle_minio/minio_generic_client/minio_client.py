from minio import Minio
from .minio_client_interface import IMinioClient
from typing import Optional
from urllib3 import HTTPResponse


class MinioClient(IMinioClient):
    def __init__(
        self,
        endpoint: str,
        access_key: Optional[str],
        secret_key: Optional[str],
        secure: bool = False,
    ):
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

    def get_client(self) -> Minio:
        return self.client

    def close_connection(self, request: HTTPResponse) -> None:
        request.close()
        request.release_conn()
