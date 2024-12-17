from flask import Flask
from flask_restful import Api
from .handle_minio.resources import GetAllMetadata, GetMetadataFromDate


def create_app():
    app = Flask(__name__)
    api = Api(app)

    @app.route("/")
    def home():
        return "Hello, World!"

    api.add_resource(GetAllMetadata, "/get_all_metadata")
    api.add_resource(GetMetadataFromDate, "/get_metadata_from_date/<string:date>")

    return app
