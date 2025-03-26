from rag_app import RagApp
from models.engine import db


def init_app(app: RagApp):
    db.init_app(app)
