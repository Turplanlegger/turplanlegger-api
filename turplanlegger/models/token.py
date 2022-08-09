import json
import datetime
from typing import Any, Dict
from urllib.request import urlopen
import jwt
from flask import current_app
from jwt import DecodeError, ExpiredSignatureError, InvalidAudienceError

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
    def parse(cls, token: str) -> 'JWT':
        jsonurl = urlopen("https://turplanlegger.b2clogin.com/turplanlegger.onmicrosoft.com/discovery/v2.0/keys?p=b2c_1_signin")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = ''
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk({
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                })
                break
        
        key = rsa_key if rsa_key else current_app.config['SECRET_KEY'] if unverified_header["kid"] == current_app.config['SECRET_KEY_ID'] else ''

        try:
            jsonRes = jwt.decode(
                token,
                key,
                algorithms=[unverified_header["alg"]],
                audience=current_app.config['AUDIENCE']
            )
        except (DecodeError, ExpiredSignatureError, InvalidAudienceError):
            raise
        
        return JWT(
            iss=jsonRes.get('iss', None),
            sub=jsonRes.get('sub', None),
            aud=jsonRes.get('aud', None),
            exp=jsonRes.get('exp', None),
            nbf=jsonRes.get('nbf', None),
            iat=jsonRes.get('iat', None),
            jti=jsonRes.get('jti', None),
            typ=jsonRes.get('typ', None)
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
        return jwt.encode(self.serialize, key=self.key, algorithm=algorithm, headers={"kid": self.kid})

    def __repr__(self) -> str:
        return (f'Jwt(iss={self.issuer}, sub={self.subject}, aud={self.audience}, '
                f'exp={self.expiration}, nbf={self.not_before}, iat={self.issued_at})'
                f'jti={self.jwt_id}, typ={self.type}')
