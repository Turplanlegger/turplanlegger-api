import re
from typing import Dict
from uuid import uuid4
from turplanlegger import auth

from turplanlegger.app import db, logger
from turplanlegger.auth import utils

JSON = Dict[str, any]


class User:

    def __init__(self, name: str, last_name: str, email: str, auth_method: str,
                 password: str, private: bool = False, **kwargs) -> None:

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

        self.id = kwargs.get('id') or str(uuid4())
        self.name = name
        self.last_name = last_name
        self.email = email
        self.auth_method = auth_method
        self.password = password
        self.private = private
        self.deleted = kwargs.get('deleted', False)
        self.delete_time = kwargs.get('delete_time', None)
        self.create_time = kwargs.get('create_time', None)

    @classmethod
    def parse(cls, json: JSON) -> 'User':
        email = json.get('email', None)
        p = re.compile('^[\\w.-]+@[\\w.-]+\\.\\w+$')
        if not p.match(email):
            raise ValueError('Invalid email address')

        if User.find_by_email(email):
            raise ValueError('User allready existst')

        auth_method = json.get('auth_method', None)
        password = json.get('password', '')
        if auth_method == 'basic':
            if not password:
                raise ValueError('Password is mandatory for auth_type basic')
            if len(password) < 3:
                raise ValueError('Password too short')
        try:
            password = utils.hash_password(password)
        except Exception as e:
            logger.exception(str(e))
            raise ValueError('Failed to create user')

        return User(
            id=json.get('id', None),
            name=json.get('name', None),
            last_name=json.get('last_name', None),
            email=email,
            auth_method=auth_method,
            password=password,
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
        self.password = self.password.decode('utf-8')  # Revise this one!
        return self.get_user(db.create_user(self))

    def rename(self) -> 'User':
        return self.get_user(db.rename_user(self))

    def delete(self) -> bool:
        return db.delete_user(self.id)

    def toggle_private(self):
        return db.toggle_private_user(self.id, False if self.private else True)

    @staticmethod
    def find_user(id: str) -> 'User':
        return User.get_user(db.get_user(id))

    @staticmethod
    def find_by_email(email: str) -> 'User':
        p = re.compile('^[\\w.-]+@[\\w.-]+\\.\\w+$')
        if not p.match(email):
            raise ValueError('invalid email address')

        return User.get_user(db.get_user_by('email', email))

    @staticmethod
    def check_credentials(email: str, password: str):
        user = User.find_by_email(email)

        if user and utils.check_password(user.password, password):
            return user
        return None

    @classmethod
    def get_user(cls, rec) -> 'User':
        if isinstance(rec, dict):
            return User(
                id=rec.get('id', None),
                name=rec.get('name', None),
                last_name=rec.get('last_name', None),
                email=rec.get('email', None),
                auth_method=rec.get('auth_method', None),
                password=rec.get('password', None),
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
                password=rec.password,
                private=rec.private,
                create_time=rec.create_time,
                deleted=rec.deleted,
                delete_time=rec.delete_time
            )
