import datetime
import jwt

from flask import current_app
from typing import Any, Dict

from turplanlegger.app import logger

JSON = Dict[str, Any]
dt = datetime.datetime


class JWT:

    def __init__(self, iss: str, sub: str, aud: str, exp: dt, nbf: dt,
                 iat: dt, jti: str, typ: str, **kwargss) -> None:

        self.issuer = iss
        self.subject = sub
        self.audience = aud
        self.expiration = exp
        self.not_before = nbf
        self.issued_at = iat
        self.jwt_id = jti
        self.type = typ

    @property
    def serialize(self) -> JSON:
        return {
            'iss': self.issuer,
            'typ': self.type,
            'sub': self.subject,
            'aud': self.audience,
            'exp': self.expiration,
            'nbf': self.not_before,
            'iat': self.issued_at,
            'jti': self.jwt_id
        }

    def tokenize(self, algorithm: str = 'HS256') -> str:
        return jwt.encode(self.serialize, key=current_app.config['SECRET_KEY'], algorithm=algorithm)
