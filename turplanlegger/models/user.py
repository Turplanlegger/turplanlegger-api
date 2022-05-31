import re

from typing import Dict
from turplanlegger.app import db

JSON = Dict[str, any]


class User:

    def __init__(self, name: str, last_name: str, email: str, auth_method: str, **kwargs) -> None:

        if not name:
            raise ValueError('Missing mandatory field \'name\'')
        if not isinstance(name, str):
            raise TypeError('\'name\' must be string')

        if not last_name:
            raise ValueError('Missing mandatory field \'last_name\'')
        if not isinstance(last_name, str):
            raise TypeError('\'last_name\' must be string')

        if not email:
            raise ValueError('Missing mandatory field \'email\'')
        if not isinstance(email, str):
            raise TypeError('\'email\' must be string')

        if not auth_method:
            raise ValueError('Missing mandatory field \'auth_method\'')

        self.name = name
        self.last_name = last_name
        self.id = kwargs.get('id', None)
        self.email = email
        self.auth_method = auth_method
        self.deleted = kwargs.get('deleted', False)
        self.deleted_time = kwargs.get('deleted_time', None)
        self.create_time = kwargs.get('create_time', None)

    @classmethod
    def parse(cls, json: JSON) -> 'User':
        email = json.get('email', None)
        p = re.compile('^((\w[^\W]+)[\.\-]?){1,}\@(([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$')
        if not p.match(email):
            raise ValueError('invalid email address')

        return User(
            name=json.get('name', None),
            last_name=json.get('last_name', None),
            email=email,
            auth_method=json.get('auth_method', None)
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'auth_method': self.auth_method,
            'deleted': self.deleted,
            'deleted_time': self.deleted_time,
            'create_time': self.create_time
        }

    @staticmethod
    def find_user(id: int) -> 'User':
        return User.get_user(db.get_user(id))

    @classmethod
    def get_user(cls, rec) -> 'User':
        if isinstance(rec, dict):
            return User(
                id=rec.get('id', None),
                name=rec.get('name', None),
                last_name=rec.get('last_name', None),
                email=rec.get('email', None),
                deleted=rec.get('deleted', False),
                deleted_time=rec.get('deleted_time', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return User(
                id=rec.id,
                name=rec.name,
                last_name=rec.last_name,
                email=rec.email,
                auth_method=rec.auth_method,
                deleted=rec.deleted,
                deleted_time=rec.deleted_time,
                create_time=rec.create_time
            )
