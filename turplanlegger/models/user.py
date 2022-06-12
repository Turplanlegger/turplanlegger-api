import re

from typing import Dict
from turplanlegger.app import db

JSON = Dict[str, any]


class User:

    def __init__(self, name: str, last_name: str, email: str, auth_method: str,
                 private: bool = False, **kwargs) -> None:

        if not isinstance(private, bool):
            raise TypeError('\'private\' must be boolean')

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

        id = kwargs.get('id', None)
        if id and not isinstance(id, int):
            raise TypeError('\'id\' must be int')

        self.id = id
        self.name = name
        self.last_name = last_name
        self.email = email
        self.auth_method = auth_method
        self.private = private
        self.deleted = kwargs.get('deleted', False)
        self.delete_time = kwargs.get('delete_time', None)
        self.create_time = kwargs.get('create_time', None)

    @classmethod
    def parse(cls, json: JSON) -> 'User':
        email = json.get('email', None)
        p = re.compile('^[\\w.-]+@[\\w.-]+\\.\\w+$')
        if not p.match(email):
            raise ValueError('invalid email address')

        return User(
            name=json.get('name', None),
            last_name=json.get('last_name', None),
            email=email,
            auth_method=json.get('auth_method', None),
            private=json.get('private', False)
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'auth_method': self.auth_method,
            'private': self.private,
            'create_time': self.create_time,
            'deleted': self.deleted,
            'delete_time': self.delete_time
        }

    def create(self) -> 'User':
        return self.get_user(db.create_user(self))

    def rename(self) -> 'User':
        return self.get_user(db.rename_user(self))

    def delete(self) -> bool:
        return db.delete_user(self.id)

    def toggle_private(self):
        return db.toggle_private_user(self.id, False if self.private else True)

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
                auth_method=rec.get('auth_method', None),
                private=rec.get('private', None),
                create_time=rec.get('created', None),
                deleted=rec.get('deleted', False),
                delete_time=rec.get('delete_time', None)
            )
        elif isinstance(rec, tuple):
            return User(
                id=rec.id,
                name=rec.name,
                last_name=rec.last_name,
                email=rec.email,
                auth_method=rec.auth_method,
                private=rec.private,
                create_time=rec.create_time,
                deleted=rec.deleted,
                delete_time=rec.delete_time
            )
