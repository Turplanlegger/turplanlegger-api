import os
from flask import Flask


class Config:

    def __init__(self, app: Flask = None) -> None:
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        config = self.get_config()
        app.config.update(config)

    def get_config(self):
        from flask import Config
        self.config = Config('/')

        config_path = os.getenv('TURPLANLEGGER_CONFIG_PATH', '/etc/turplanlegger/turplanlegger.conf')
        self.config.from_pyfile(config_path)

        # Database
        self.config['DATABASE_URI'] = self.conf_ent('DATABASE_URI')
        self.config['DATABASE_NAME'] = self.conf_ent('DATABASE_NAME')
        self.config['DATABASE_MAX_RETRIES'] = self.conf_ent('DATABASE_MAX_RETRIES', 5)

        # Logging
        self.config['LOG_FILE'] = self.conf_ent(
            'LOG_FILE', '/var/log/turplanlegger.log')
        self.config['LOG_LEVEL'] = self.conf_ent('LOG_LEVEL', 'INFO')

        return self.config

    def conf_ent(self, key, default=None):
        rv = self.config.get(key, default)

        if not rv and not default:
            raise RuntimeError(
                f'Config entry {key} is required, please set it')

        return rv
