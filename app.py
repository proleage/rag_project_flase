from gevent import monkey  # type: ignore

# gevent
monkey.patch_all()

from grpc.experimental import gevent as grpc_gevent  # type: ignore

# grpc gevent
grpc_gevent.init_gevent()

import psycogreen.gevent  # type: ignore

psycogreen.gevent.patch_psycopg()

from app_factory import create_app

app = create_app()

celery = app.extensions["celery"]


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run("0.0.0.0", 5000)
