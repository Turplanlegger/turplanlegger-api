import logging
from sys import stdout

from flask import Flask


class Logger:

    def __init__(self, app: Flask = None) -> None:
        self.app = None
        if app:
            self.setup_logging(app)

    def setup_logging(self, app: Flask = None) -> None:
        log_level = app.config.get('LOG_LEVEL')
        log_format = '%(asctime)s - %(name)s: %(levelname)s - %(message)s'
        if app.debug:
            log_level = 'DEBUG'
            log_format = ('%(asctime)s - %(name)s[%(process)d]: %(levelname)s '
                          '- %(message)s [in %(pathname)s:%(lineno)d]')
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(app.config.get('LOG_FILE')),
                logging.StreamHandler(stdout)
            ]
        )

