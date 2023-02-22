import datetime
from typing import Any, Dict

import jwt
from flask import current_app
from httpx import HTTPError
from jwt import DecodeError, ExpiredSignatureError, InvalidAudienceError

from turplanlegger.models.user import User

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
        unverified_header = jwt.get_unverified_header(token)
        key = cls.find_correct_key(token, unverified_header)

        try:
            jsonRes = jwt.decode(
                token,
                key,
                algorithms=[unverified_header['alg']],
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

    @classmethod
    def parse_user_from_token(cls, token: str) -> User:
        unverified_header = jwt.get_unverified_header(token)
        key = cls.find_correct_key(token, unverified_header)

        try:
            jsonRes = jwt.decode(
                token,
                key,
                algorithms=[unverified_header['alg']],
                audience=current_app.config['AUDIENCE']
            )
        except (DecodeError, ExpiredSignatureError, InvalidAudienceError):
            raise

        return User(
            id=jsonRes.get('sub', None),
            name=jsonRes.get('given_name', None),
            last_name=jsonRes.get('family_name', None),
            email=jsonRes.get('emails', None)[0],
            auth_method='b2c',
            password=''
        )

    def find_correct_key(token: str, unverified_header: str) -> str:
        try:
            response = current_app.http_client.get(
                current_app.config['AZURE_AD_B2C_KEY_URL']
            )
            response.raise_for_status()
        except HTTPError:
            raise

        jwks = response.json()
        rsa_key = ''

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk({
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                })
                break

        if (rsa_key):
            key = rsa_key
        elif (unverified_header['kid'] == current_app.config['SECRET_KEY_ID']):
            key = current_app.config['SECRET_KEY']
        else:
            key = ''

        return key

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
        return jwt.encode(
            self.serialize,
            key=current_app.config['SECRET_KEY'],
            algorithm=algorithm,
            headers={'kid': current_app.config['SECRET_KEY_ID']})

    def __repr__(self) -> str:
        return (f'Jwt(iss={self.issuer}, sub={self.subject}, '
                f'aud={self.audience}, exp={self.expiration}, '
                f'nbf={self.not_before}, iat={self.issued_at} '
                f'jti={self.jwt_id}, typ={self.type})')
