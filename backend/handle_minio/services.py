from os import getenv
from dotenv import load_dotenv
from .minio_generic_client.minio_client import MinioClient
from urllib3.response import BaseHTTPResponse
from urllib3.exceptions import MaxRetryError

load_dotenv()


class MetadataService:
    def get_all_metadata(self) -> BaseHTTPResponse:
        try:
            client = MinioClient(
                endpoint=getenv("MINIO_BACKEND_ENDPOINT") or "MINIO_BACKEND_ENDPOINT",
                access_key=getenv("MINIO_ACCESS_KEY"),
                secret_key=getenv("MINIO_SECRECT_KEY"),
                secure=False,
            ).get_client()

            return client.get_object(
                bucket_name=getenv("MINIO_BUCKET_NAME", "MINIO_BUCKET_NAME not found."),
                object_name="Portalnoticiasceara/2024-12-14/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")

    def get_metadata_from_date(self, date: str) -> BaseHTTPResponse:
        try:
            client = MinioClient(
                endpoint=getenv("MINIO_BACKEND_ENDPOINT") or "MINIO_BACKEND_ENDPOINT",
                access_key=getenv("MINIO_ACCESS_KEY"),
                secret_key=getenv("MINIO_SECRECT_KEY"),
                secure=False,
            ).get_client()

            return client.get_object(
                bucket_name=getenv("MINIO_BUCKET_NAME", "MINIO_BUCKET_NAME not found."),
                object_name=f"Portalnoticiasceara/{date}/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")
