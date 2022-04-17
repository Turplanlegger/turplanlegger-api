from typing import Any, Dict

from flask import Flask

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
    app.config['ENVIRONMENT'] = environment
    config.init_app(app)
    app.config.update(config_override or {})

    logger.setup_logging(app)

    handlers.register(app)

    db.init_db(app)

    # from turplanlegger.views import api
    # app.register_blueprint(api)

    return app
