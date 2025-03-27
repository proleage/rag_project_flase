from flask import Blueprint

from libs.external_api import ExternalApi


from .files import FileApi
from .robert_rag import RbtRAGApi

bp = Blueprint("console", __name__, url_prefix="/api")
api = ExternalApi(bp)

# File
api.add_resource(FileApi, "/files/upload")

# RbtRAG
api.add_resource(RbtRAGApi, "/rbt_rag/query")

