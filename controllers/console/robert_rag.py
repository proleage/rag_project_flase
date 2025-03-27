import logging

from flask_login import current_user  # type: ignore
from flask_restful import Resource, marshal_with, reqparse  # type: ignore

from configs import rag_config
from extensions.ext_rbtrag import RbtRAG

PREVIEW_WORDS_LIMIT = 3000

logger = logging.getLogger(__name__)


class RbtRAGApi(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("question", type=str, required=True, location="json")
        parser.add_argument("output_filename", type=str, required=True, location="json")
        parser.add_argument(
            "model_type", type=str, required=False, default="o3-mini", location="json"
        )
        parser.add_argument(
            "database_type", type=str, required=False, default="milvus", location="json"
        )
        parser.add_argument(
            "reranking_type", type=str, required=False, default=None, location="json"
        )
        parser.add_argument(
            "collection_name", type=str, required=False, default="my_rag_collection", location="json"
        )
        parser.add_argument("k", type=int, required=False, default=50, location="json")

        args = parser.parse_args()

        question = args["question"]
        output_filename = args["output_filename"]
        model_type = args["model_type"]
        database_type = args["database_type"]
        reranking_type = args["reranking_type"]
        collection_name = args["collection_name"]
        k = args["k"]

        rbt_rag = RbtRAG.RagasService(
            question=question,
            output_filename=output_filename,
            model_type=model_type,
            database_type=database_type,
            reranking_type=reranking_type,
            k=k,
            collection_name=collection_name
        )
        rbt_rag.start()

        output_filename = (
            f"{rag_config.BASE_DIR}{rag_config.DATA_OUTPUT_DIR}/{output_filename}.md"
        )

        try:
            with open(output_filename, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            return {"error": f"读取文件失败：{str(e)}"}, 500

        return {"content": file_content}, 201
