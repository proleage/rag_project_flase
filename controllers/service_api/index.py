from flask_restful import Resource  # type: ignore

from configs import rag_config
from controllers.service_api import api


class IndexApi(Resource):
    def get(self):
        return {
            "welcome": "Dify OpenAPI",
            "api_version": "v1",
            "server_version": rag_config.CURRENT_VERSION,
        }


api.add_resource(IndexApi, "/")