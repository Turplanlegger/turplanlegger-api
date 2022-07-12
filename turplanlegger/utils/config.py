import os
from os.path import exists
from typing import Any, Dict

from flask import Flask


class Config:

    def __init__(self, app: Flask = None) -> None:
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask, override: Dict[str, Any]) -> None:
        config = self.get_config(override)
        app.config.update(config)

    def get_config(self, override: Dict[str, Any]):
        from flask import Config
        self.config = Config('/')

        # Read default config
        current_dir_path = os.path.dirname(os.path.abspath(__file__))
        default_config_path = current_dir_path + '/default_config.py'
        self.config.from_pyfile(default_config_path)

        # Override config if other configfile exists
        config_path = os.getenv('TURPLANLEGGER_CONFIG_PATH', '/etc/turplanlegger/turplanlegger.conf')
        if (exists(config_path)):
            self.config.from_pyfile(config_path)

        if override:
            for key, value in override.items():
                self.config[key] = value

        # App
        self.config['SECRET_KEY'] = self.conf_ent('SECRET_KEY')
        self.config['TOKEN_EXPIRE_TIME'] = self.conf_ent('TOKEN_EXPIRE_TIME')  # Seconds
        self.config['CREATE_ADMIN_USER'] = self.conf_ent('CREATE_ADMIN_USER', False)
        if self.config['CREATE_ADMIN_USER']:
            self.config['ADMIN_EMAIL'] = self.conf_ent('ADMIN_EMAIL', 'test@test.com')
            self.config['ADMIN_PASSWORD'] = self.conf_ent('ADMIN_PASSWORD', 'admin')

        # Database
        self.config['DATABASE_URI'] = self.conf_ent('DATABASE_URI')
        self.config['DATABASE_NAME'] = self.conf_ent('DATABASE_NAME')
        self.config['DATABASE_MAX_RETRIES'] = self.conf_ent('DATABASE_MAX_RETRIES', 5)

        # Logging
        log_path = os.getenv('TURPLANLEGGER_LOG_PATH', '/var/log/turplanlegger.log')
        self.config['LOG_FILE'] = self.conf_ent(
            'LOG_FILE', log_path)
        self.config['LOG_LEVEL'] = self.conf_ent('LOG_LEVEL', 'INFO')

        return self.config

    def conf_ent(self, key, default=None):
        rv = self.config.get(key, default)

        if rv is None:
            raise RuntimeError(
                f'Config entry {key} is required, please set it')

        return rv
