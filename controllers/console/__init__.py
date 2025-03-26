from flask import Blueprint

from libs.external_api import ExternalApi


from .files import FileApi


bp = Blueprint("console", __name__, url_prefix="/api")
api = ExternalApi(bp)

# File
api.add_resource(FileApi, "/files/upload")

