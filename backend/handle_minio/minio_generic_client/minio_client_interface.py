from abc import ABC, abstractmethod
from minio import Minio
from urllib3 import HTTPResponse


class IMinioClient(ABC):
    @abstractmethod
    def get_client(self) -> Minio:
        pass

    def close_connection(self, request: HTTPResponse) -> None:
        pass
