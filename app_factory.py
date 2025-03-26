import logging
import time

from configs import rag_config
from contexts.wrapper import RecyclableContextVar
from rag_app import RagApp


# ----------------------------
# Application Factory Function
# ----------------------------
def create_flask_app_with_configs() -> RagApp:
    """
    create a raw flask app
    with configs loaded from .env file
    """
    rag_app = RagApp(__name__)
    rag_app.config.from_mapping(rag_config.model_dump())

    # add before request hook
    @rag_app.before_request
    def before_request():
        # add an unique identifier to each request
        RecyclableContextVar.increment_thread_recycles()

    return rag_app


def initialize_extensions(app: RagApp):
    from extensions import (ext_blueprints, ext_celery, ext_database,
                            ext_logging, ext_login, ext_redis, ext_storage,
                            ext_timezone, ext_warnings)

    extensions = [
        ext_timezone,
        ext_storage,
        ext_celery,
        ext_logging,
        ext_warnings,
        ext_blueprints,
        ext_database,
        ext_login,
        ext_redis,
    ]
    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if rag_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue

        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if rag_config.DEBUG:
            logging.info(
                f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)"
            )


def create_app() -> RagApp:
    start_time = time.perf_counter()
    app = create_flask_app_with_configs()
    initialize_extensions(app)
    end_time = time.perf_counter()
    if rag_config.DEBUG:
        logging.info(
            f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)"
        )
    return app
