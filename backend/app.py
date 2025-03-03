from flask import Flask
from flask_restful import Api
from .handle_minio.resources import (
    Home,
    GetDailyMetadata,
    GetMetadataFromDate,
    GetMonthlyMetadata,
    GetWeeklyMetadata,
    GetMetadataFromLocation,
)


def create_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Home, "/")
    api.add_resource(GetDailyMetadata, "metadata/daily")
    api.add_resource(GetWeeklyMetadata, "metadata/weekly")
    api.add_resource(GetMonthlyMetadata, "metadata/monthly")
    api.add_resource(GetMetadataFromDate, "metadata/date/<string:date>")
    api.add_resource(
        GetMetadataFromLocation,
        "metadata/location/<string:state>/<string:city>/<string:neigborhood>/<string:street>",
    )

    return app
