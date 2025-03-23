import re
from typing import Dict, NamedTuple
from uuid import UUID, uuid4

from turplanlegger.app import db, logger
from turplanlegger.auth import utils
from turplanlegger.utils.types import to_uuid

JSON = Dict[str, any]


class User:
    """A User object. Used for setting owner and sharing content

    Args:
        name (str): First name of the user
        last_name (str): Last name/sir name of the user
        email (str): Email of the user
        password (str): Hashed password of the user
                        Only used for basic auth
        private (bool): Flag if the user should be private or public
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (UUID): Optional, the ID of the object
        name (str): First name of the user
        last_name (str): Last name/sir name of the user
        email (str): Email of the user
        password (str): Hashed password of the user
                        Only used for basic auth
        private (bool): Flag if the user should be private or public
        deleted (bool): Flag if the user has logicaly been deleted
        delete_time (datetime): Time of the deletion of the user
        create_time (datetime): Time of creation,
                                Default: datetime.now()
    """

    def __init__(
        self, name: str, last_name: str, email: str, auth_method: str, password: str, private: bool = False, **kwargs
    ) -> None:
        if not isinstance(private, bool):
            raise TypeError("'private' must be boolean")

        if not name:
            raise ValueError("Missing mandatory field 'name'")
        if not isinstance(name, str):
            raise TypeError("'name' must be string")

        if not last_name:
            raise ValueError("Missing mandatory field 'last_name'")
        if not isinstance(last_name, str):
            raise TypeError("'last_name' must be string")

        if not email:
            raise ValueError("Missing mandatory field 'email'")
        if not isinstance(email, str):
            raise TypeError("'email' must be string")

        if not auth_method:
            raise ValueError("Missing mandatory field 'auth_method'")


        self.id = kwargs.get('id') or uuid4()
        self.name = name
        self.last_name = last_name
        self.email = email
        self.auth_method = auth_method
        self.password = password
        self.private = private
        self.deleted = kwargs.get('deleted', False)
        self.delete_time = kwargs.get('delete_time', None)
        self.create_time = kwargs.get('create_time', None)

    def __repr__(self):
        return (
            f"User(id={self.id}, name='{self.name}', last_name='{self.last_name}', "
            f"email='{self.email}', auth_method={self.auth_method}, "
            f'private={self.private}, deleted={self.deleted}, '
            f'delete_time={self.delete_time}, create_time={self.create_time})'
        )

    def __setattr__(self, name, value):
        if name == 'id':
            self.__dict__[name] = to_uuid(value)
        else:
            self.__dict__[name] = value

    @classmethod
    def parse(cls, json: JSON) -> 'User':
        """Parse input JSON and return an User instance.
        Checks if the email matches email-format regex
        Checks length of password if auth_type is basic
        Hashes password

        Args:
            json (Dict[str, any]): JSON input object

        Raises:
            ValueError:
                On failed email format rexeg match
                If user already exists (checked by email)
                If password isn't supplied when auth_type is basic
                If password is too short when auth_type is basic
                If the password hashing failed

        Returns:
            A Route object
        """
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
            private=json.get('private', False),
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the User instance, returns it as Dict(str, any)"""
        return {
            'id': str(self.id),
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'auth_method': self.auth_method,
            'private': self.private,
            'create_time': self.create_time,
            'deleted': self.deleted,
            'delete_time': self.delete_time,
        }

    def create(self) -> 'User':
        """Creates the Route object in the database
        will also decode the hased password to a UTF-8 string"""
        self.password = self.password.decode('utf-8') if (self.password != '') else None  # Revise this one!
        return self.get_user(db.create_user(self))

    def rename(self) -> 'User':
        """Update name and last name
        Returns an updated instance of the user"""
        return self.get_user(db.rename_user(self))

    def delete(self) -> bool:
        """Deletes the Route object from the database
        Returns True if deleted"""
        return db.delete_user(self.id)

    def toggle_private(self) -> 'None':
        """Switch the privacy of the user"""
        return db.toggle_private_user(self.id, False if self.private else True)

    @staticmethod
    def find_user(id: UUID) -> 'User':
        """Looks up an user based on id

        Args:
            id (UUID): Id (uuid4) of user

        Returns:
            An User instance
        """
        return User.get_user(db.get_user(id))

    @staticmethod
    def find_by_email(email: str) -> 'User':
        """Looks up an user based on email

        Args:
            email (str): Email to look for

        Raises:
            ValueError:
                On failed email format rexeg match

        Returns:
            A User instance
        """
        p = re.compile('^[\\w.-]+@[\\w.-]+\\.\\w+$')
        if not p.match(email):
            raise ValueError('invalid email address')

        return User.get_user(db.get_user_by('email', email))

    @staticmethod
    def check_credentials(email: str, password: str):
        """Looks up a user by email and checkes passed password
        if it matches the on in the database.

        Args:
            email (str): Email to look for
            passowrd (str): Unhashed password

        Returns:
            A user instance if user is found and password matches
            None if not
        """
        user = User.find_by_email(email)

        if user and utils.check_password(user.password, password):
            return user

        return None

    @classmethod
    def get_user(cls, rec: NamedTuple) -> 'User':
        """Converts a database record to an User instance

        Args:
            rec (NamedTuple): Database record

        Returns:
            An User instance
        """
        if rec is None:
            return None

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
            delete_time=rec.delete_time,
        )
