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

        # Load custom config file
        config_path = os.getenv('TP_CONFIG_PATH', '/etc/turplanlegger/turplanlegger.conf')
        if (exists(config_path)):
            self.config.from_pyfile(config_path)

        if override:
            for key, value in override.items():
                self.config[key] = value

        # App
        self.config['SECRET_KEY'] = self.conf_ent('SECRET_KEY', str)
        self.config['SECRET_KEY_ID'] = self.conf_ent('SECRET_KEY_ID', str)
        self.config['AUDIENCE'] = self.conf_ent('AUDIENCE', str, '0149fc65-259e-4895-9034-e144c242f733')
        self.config['AZURE_AD_B2C_KEY_URL'] = self.conf_ent(
            'AZURE_AD_B2C_KEY_URL',
            str,
            'https://turplanlegger.b2clogin.com/turplanlegger.onmicrosoft.com/discovery/v2.0/keys?p=b2c_1_signin'
        )
        self.config['TOKEN_EXPIRE_TIME'] = self.conf_ent('TOKEN_EXPIRE_TIME', int, 86400)  # Seconds
        self.config['CREATE_ADMIN_USER'] = self.conf_ent('CREATE_ADMIN_USER', bool, False)
        if self.config['CREATE_ADMIN_USER']:
            self.config['ADMIN_EMAIL'] = self.conf_ent('ADMIN_EMAIL', str, 'test@test.com')
            self.config['ADMIN_PASSWORD'] = self.conf_ent('ADMIN_PASSWORD', str, 'admin')

        # Database
        self.config['DATABASE_URI'] = self.conf_ent('DATABASE_URI', str)
        self.config['DATABASE_NAME'] = self.conf_ent('DATABASE_NAME', str, 'turplanlegger')
        self.config['DATABASE_MAX_RETRIES'] = self.conf_ent('DATABASE_MAX_RETRIES', int, 5)
        self.config['DATABASE_MIN_POOL_SIZE'] = self.conf_ent('DATABASE_MIN_POOL_SIZE', int, 2)
        self.config['DATABASE_MAX_POOL_SIZE'] = self.conf_ent('DATABASE_MAX_POOL_SIZE', int, 10)
        self.config['DATABASE_TIMEOUT'] = self.conf_ent('DATABASE_TIMEOUT', int, 10)
        self.config['DATABASE_MAX_WAITING'] = self.conf_ent('DATABASE_MAX_WAITING', int, 0)
        self.config['DATABASE_MAX_LIFETIME'] = self.conf_ent('DATABASE_MAX_LIFETIME', int, 1800)
        self.config['DATABASE_MAX_IDLE'] = self.conf_ent('DATABASE_MAX_IDLE', int, 300)
        self.config['DATABASE_RECONNECT_TIMEOUT'] = self.conf_ent('DATABASE_RECONNECT_TIMEOUT', int, 90)
        self.config['DATABASE_CONNECTION_TEST_TIMEOUT'] = self.conf_ent('DATABASE_CONNECTION_TEST_TIMEOUT', int, 1)

        # Logging
        self.config['LOG_LEVEL'] = self.conf_ent('LOG_LEVEL', str, 'INFO')
        self.config['LOG_TO_FILE'] = self.conf_ent('LOG_TO_FILE', bool, False)
        if self.config['LOG_TO_FILE']:
            self.config['LOG_PATH'] = self.conf_ent(
                'LOG_PATH',
                str,
                '/var/log/turplanlegger.log'
            )

        self.config['CORS_ORIGINS'] = self.conf_ent('CORS_ORIGINS', list, ['http://localhost:3000'])

        return self.config

    def conf_ent(self, key, ent_type=None, default=None):
        """Get and check config entry
        Looks for config entry in environment variable by
        key prepended with 'TP_'.
        If config entry is found in environment variable, convert from
        string to bool, int, list or tuple.

        Args:
            key (str): Config key
            ent_type (instance): Expected instance of config value
                                 Default: None
            default (Any): The default value of the config entry

        Returns:
            rv: Config value
        """
        envar = f'TP_{key}'

        if envar in os.environ:
            rv = os.environ.get(envar, default)
            if ent_type is bool:
                if key.lower() in ['no', 'false', 'nei', '0']:
                    rv = False
                if key.lower() in ['yes', 'true', 'ja', '1']:
                    rv = True
            if ent_type is int:
                try:
                    rv = int(rv)
                except ValueError:
                    raise RuntimeError(
                        f'Config entry {key} is has to be int'
                    )
            if ent_type in [list, tuple]:
                rv = rv.split(',')
            if ent_type is tuple:
                rv = tuple(rv)
        else:
            rv = self.config.get(key, default)

        if rv is None:
            raise RuntimeError(
                f'Config entry {key} is required, please set it'
            )

        return rv
