from os import getenv
from dotenv import load_dotenv
from .services import MetadataService
from flask_restful import Resource

load_dotenv()


class BaseMetadataResource(Resource):
    def __init__(self) -> None:
        self.endpoint = getenv(
            "MINIO_BACKEND_ENDPOINT", "MINIO_BACKEND_ENDPOINT not found in .env file"
        )
        self.access_key = getenv(
            "MINIO_ACCESS_KEY", "MINIO_ACCESS_KEY not found in .env file"
        )
        self.secret_key = getenv(
            "MINIO_SECRET_KEY", "MINIO_SECRET_KEY not found in .env file"
        )
        self.bucket_name = getenv(
            "MINIO_BUCKET_NAME", "MINIO_BUCKET_NAME not found in .env file"
        )
        self.secure = False


class GetDailyMetadata(BaseMetadataResource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        try:
            response = MetadataService(
                self.endpoint,
                self.access_key,
                self.secret_key,
                self.bucket_name,
                self.secure,
            ).get_daily_metadata()
            return response.json()
        except Exception as e:
            return {"error": str(e)}, 500


class GetMetadataFromDate(BaseMetadataResource):
    def __init__(self) -> None:
        super().__init__()

    def get(self, date: str):
        try:
            response = MetadataService(
                self.endpoint,
                self.access_key,
                self.secret_key,
                self.bucket_name,
                self.secure,
            ).get_metadata_from_date(date)
            return response.json()
        except Exception as e:
            return {"error": str(e)}, 500


class GetMonthlyMetadata(BaseMetadataResource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        try:
            response = MetadataService(
                self.endpoint,
                self.access_key,
                self.secret_key,
                self.bucket_name,
                self.secure,
            ).get_monthly_metadata()
            return response.json()
        except Exception as e:
            return {"error": str(e)}, 500


class GetLastSevenDaysMetadata(BaseMetadataResource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        try:
            response = MetadataService(
                self.endpoint,
                self.access_key,
                self.secret_key,
                self.bucket_name,
                self.secure,
            ).get_last_seven_days_metadata()
            return response.json()
        except Exception as e:
            return {"error": str(e)}, 500


class GetMetadataFromLocation(BaseMetadataResource):
    def __init__(self) -> None:
        super().__init__()

    def get(self, state: str, city: str, neigborhood: str, street: str):
        try:
            response = MetadataService(
                self.endpoint,
                self.access_key,
                self.secret_key,
                self.bucket_name,
                self.secure,
            ).get_metadata_from_location(state, city, neigborhood, street)
            return response.json()
        except Exception as e:
            return {"error": str(e)}, 500
