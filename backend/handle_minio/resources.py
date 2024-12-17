from .services import MetadataService
from flask_restful import Resource


class GetAllMetadata(Resource):
    def get(self):
        response = MetadataService().get_all_metadata()
        return response.json()


class GetMetadataFromDate(Resource):
    def get(self, date: str):
        response = MetadataService().get_metadata_from_date(date)
        return response.json()
