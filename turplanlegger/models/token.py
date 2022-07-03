import datetime
import jwt

from flask import current_app
from jwt import DecodeError, ExpiredSignatureError, InvalidAudienceError
from typing import Any, Dict

JSON = Dict[str, Any]
dt = datetime.datetime


class JWT:

    def __init__(self, iss: int, sub: str, aud: str, exp: dt, nbf: dt,
                 iat: dt, jti: str, typ: str, **kwargss) -> None:

        self.issuer = iss
        self.subject = sub
        self.audience = aud
        self.expiration = exp
        self.not_before = nbf
        self.issued_at = iat
        self.jwt_id = jti
        self.type = typ

    @classmethod
    def parse(cls, token: str, algorithm: str = 'HS256') -> 'JWT':
        try:
            json = jwt.decode(
                    token,
                    key=current_app.config['SECRET_KEY'],
                    options={'verify_signature': True},
                    algorithms=[algorithm],
                    audience='/'
                )
        except (DecodeError, ExpiredSignatureError, InvalidAudienceError):
            raise

        return JWT(
            iss=json.get('iss', None),
            sub=json.get('sub', None),
            aud=json.get('aud', None),
            exp=json.get('exp', None),
            nbf=json.get('nbf', None),
            iat=json.get('iat', None),
            jti=json.get('jti', None),
            typ=json.get('typ', None)
        )

    @property
    def serialize(self) -> JSON:
        return {
            'iss': self.issuer,
            'sub': self.subject,
            'aud': self.audience,
            'exp': self.expiration,
            'nbf': self.not_before,
            'iat': self.issued_at,
            'jti': self.jwt_id,
            'typ': self.type
        }

    def tokenize(self, algorithm: str = 'HS256') -> str:
        return jwt.encode(self.serialize, key=current_app.config['SECRET_KEY'], algorithm=algorithm)

    def __repr__(self) -> str:
        return (f'Jwt(iss={self.issuer}, sub={self.subject}, aud={self.audience}, '
                f'exp={self.expiration}, nb={self.not_before}, iat={self.issued_at})'
                f'jti={self.jwt_id}, typ={self.type}')
