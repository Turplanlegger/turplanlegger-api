from typing import Any, Dict

from flask import Flask
from flask_cors import CORS

from turplanlegger.database.base import Database
from turplanlegger.exceptions import ExceptionHandlers
from turplanlegger.utils.config import Config
from turplanlegger.utils.logger import Logger

handlers = ExceptionHandlers()
config = Config()
logger = Logger()
db = Database()


def create_app(config_override: Dict[str, Any] = None,
               environment: str = None) -> Flask:

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    app.config['ENVIRONMENT'] = environment
    config.init_app(app, config_override)

    logger.setup_logging(app)

    handlers.register(app)

    db.init_db(app)

    from turplanlegger.views import api
    app.register_blueprint(api)

    from turplanlegger.auth import auth
    app.register_blueprint(auth)

    return app
