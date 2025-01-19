from .minio_generic_client.minio_client import MinioClient
from urllib3.response import BaseHTTPResponse
from urllib3.exceptions import MaxRetryError


class MetadataServices:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ) -> None:
        self.__service__ = MinioClient(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

        self.bucket_name = bucket_name

    def get_daily_metadata(self) -> BaseHTTPResponse:
        try:
            client = self.__service__.get_client()

            return client.get_object(
                bucket_name=self.bucket_name,
                object_name="Portalnoticiasceara/noticias_recentes_ultimas_24_horas/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")

    def get_metadata_from_date(self, date: str) -> BaseHTTPResponse:
        try:
            client = self.__service__.get_client()

            return client.get_object(
                bucket_name=self.bucket_name,
                object_name=f"Portalnoticiasceara/past_dates/{date}/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")

    def get_monthly_metadata(self) -> BaseHTTPResponse:
        try:
            client = self.__service__.get_client()

            return client.get_object(
                bucket_name=self.bucket_name,
                object_name="Portalnoticiasceara/noticias_recentes_ultimo_mes/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")

    def get_last_seven_days_metadata(self) -> BaseHTTPResponse:
        try:
            client = self.__service__.get_client()

            return client.get_object(
                bucket_name=self.bucket_name,
                object_name="Portalnoticiasceara/noticias_recentes_ultimos_7_dias/metadata.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")

    def get_metadata_from_location(
        self, state: str, city: str, neighborhood: str, street: str
    ) -> BaseHTTPResponse:
        try:
            client = self.__service__.get_client()

            return client.get_object(
                bucket_name=self.bucket_name,
                object_name=f"Portalnoticiasceara/uf/{state}/{city}/{neighborhood}/{street}.json",
            )
        except MaxRetryError as e:
            raise Exception(f"Máximo de tentativas atingido: {e}")
