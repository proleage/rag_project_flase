import os
import time

from rag_app import RagApp


def init_app(app: RagApp):
    os.environ["TZ"] = "UTC"
    # windows platform not support tzset
    if hasattr(time, "tzset"):
        time.tzset()
