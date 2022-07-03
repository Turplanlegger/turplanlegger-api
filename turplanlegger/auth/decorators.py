from functools import wraps

from flask import current_app, g, request
from jwt import DecodeError, ExpiredSignatureError, InvalidAudienceError

from turplanlegger.exceptions import AuthError
from turplanlegger.models.token import JWT
from turplanlegger.models.user import User


def auth(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)

        try:
            auth_header = auth_header.split()
        except AttributeError as e:
            current_app.logger.exception(str(e))
            raise AuthError('must supply token by Authorization header', 401)

        if (len(auth_header) == 2 and
                auth_header[0] == 'Bearer' and auth_header[1]):
            token = auth_header[1]
            current_app.logger.debug(f'Supplied API token: {token}')
        else:
            raise AuthError(
                'must supply token by Authorization header', 401)

        try:
            jwt = JWT.parse(token)
        except DecodeError:
            raise AuthError('Token is invalid', 401)
        except ExpiredSignatureError:
            raise AuthError('Token has expired', 401)
        except InvalidAudienceError:
            raise AuthError('Token has invalid audience', 401)

        user = User.find_user(jwt.subject)

        if user.deleted:
            raise AuthError('Inactive user', 401)

        current_app.logger.debug(f'user {user.id} logged in')
        g.user = user

        return func(*args, **kwargs)
    return wrapped
