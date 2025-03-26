from rag_app import RagApp


def init_app(app: RagApp):
    import warnings

    warnings.simplefilter("ignore", ResourceWarning)
