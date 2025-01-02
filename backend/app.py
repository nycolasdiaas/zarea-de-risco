from flask import Flask
from flask_restful import Api
from .handle_minio.resources import (
    GetDailyMetadata,
    GetMetadataFromDate,
    GetMonthlyMetadata,
    GetLastSevenDaysMetadata,
    GetMetadataFromLocation,
)


def create_app():
    app = Flask(__name__)
    api = Api(app)

    @app.route("/")
    def home():
        return "Hello, World!"

    api.add_resource(GetDailyMetadata, "/get_daily_metadata")
    api.add_resource(GetMetadataFromDate, "/get_metadata_from_date/<string:date>")
    api.add_resource(GetMonthlyMetadata, "/get_monthly_metadata")
    api.add_resource(GetLastSevenDaysMetadata, "/get_last_seven_days")
    api.add_resource(
        GetMetadataFromLocation,
        "/get_metadata_from_location/<string:state>/<string:city>/<string:neigborhood>/<string:street>",
    )

    return app
