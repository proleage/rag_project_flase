from rag_app import RagApp
import RbtRAG_sdk


RbtRAG = RbtRAG_sdk
def init_app(app: RagApp):
    app.extensions["rbt_rag"] = RbtRAG
