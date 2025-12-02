from dataclasses import dataclass
from os import environ
from typing import Any, Dict


@dataclass(frozen=True, repr=False)
class Config:
    debug: bool
    secret_key: str
    secret_key_id: str
    audience: str
    azure_ad_b2c_key_url: str
    token_expire_time: str
    create_admin_user: bool
    admin_email: str
    admin_password: str
    database_uri: str
    database_max_retries: int
    database_timeout: int
    log_level: str
    log_to_file: bool
    log_file_path: str
    cors_origins: tuple

    @classmethod
    def from_env(cls) -> 'Config':

        return cls(
            debug=Config.get_config_val('DEBUG', bool, False),
            secret_key=Config.get_config_val('SECRET_KEY', str, required=True),
            secret_key_id=Config.get_config_val('SECRET_KEY_ID', str, required=True),
            audience=Config.get_config_val('AUDIENCE', str, '0149fc65-259e-4895-9034-e144c242f733', required=True),
            azure_ad_b2c_key_url=Config.get_config_val('AZURE_AD_B2C_KEY_URL', str, 'https://turplanlegger.b2clogin.com/turplanlegger.onmicrosoft.com/discovery/v2.0/keys?p=b2c_1_signin', required=True),
            token_expire_time=Config.get_config_val('TOKEN_EXPIRE_TIME', int, 86400, required=True),
            create_admin_user=Config.get_config_val('CREATE_ADMIN_USER', bool, False),
            admin_email=Config.get_config_val('ADMIN_EMAIL', str),
            admin_password=Config.get_config_val('ADMIN_PASSWORD', str),
            database_uri=Config.get_config_val('DATABASE_URI', str, required=True),
            database_max_retries=Config.get_config_val('DATABASE_MAX_RETRIES', int, 5, True),
            database_timeout=Config.get_config_val('DATABASE_TIMEOUT', int, 10, True),
            log_level=Config.get_config_val('LOG_LEVEL', str, 'WARNING', required=True).upper(),
            log_to_file=Config.get_config_val('LOG_TO_FILE', bool, False),
            log_file_path=Config.get_config_val('LOG_FILE_PATH', bool),
            cors_origins=Config.get_config_val('CORS_ORIGINS', tuple, tuple('http://localhost:3000'), required=True)
        )

    @staticmethod
    def get_config_val(
        key: str,
        ent_type: bool | int | list | tuple | str,
        default: bool | int | list | tuple | str | None = None,
        required: bool = False,
    ):
        """Read config entry from environment variable, prefixed with `TP_`"""
        envar = f'TP_{key}'

        val = environ.get(envar, default)
        if isinstance(ent_type, bool) and not isinstance(val, bool):
            if key.lower() in ['no', 'false', 'nei', '0']:
                return False
            if key.lower() in ['yes', 'true', 'ja', '1']:
                return True
        if ent_type is int:
            try:
                return int(val)
            except ValueError:
                raise RuntimeError(f'Config entry {key} has to be int')
        if ent_type is tuple and not isinstance(val, tuple):
            return tuple(val.split(','))
        if ent_type is list and not isinstance(val, list):
            return val.split(',')

        if required is True and not val:
            raise RuntimeError(f'Config entry {key} is required, please set it')

        return val


config = Config.from_env()
