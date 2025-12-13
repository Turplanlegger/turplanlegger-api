from flask import Flask

from turplanlegger.database.base import Database
from turplanlegger.exceptions import ExceptionHandlers
from turplanlegger.utils.cors import Cors
from turplanlegger.utils.http_client import HttpClient

handlers = ExceptionHandlers()
db = Database()
cors = Cors()
http_client = HttpClient()


def create_app() -> Flask:
    app = Flask(__name__)

    handlers.register(app)

    http_client.init_app(app)

    db.init_db(app)

    cors.init_app(app)

    from turplanlegger.views import api

    app.register_blueprint(api)

    from turplanlegger.auth import auth

    app.register_blueprint(auth)

    return app
