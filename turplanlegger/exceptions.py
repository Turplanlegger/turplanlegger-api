import traceback
from typing import Any, Dict, Tuple, Union

from flask import Response, current_app, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RoutingException


class BaseError(Exception):
    code = 500
    description = 'Unhandled exception'

    def __init__(self, message, code=None, errors=None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.errors = errors


class AuthError(BaseError):
    pass


class ApiError(BaseError):
    pass


class ExceptionHandlers:

    def register(self, app):
        from werkzeug.exceptions import default_exceptions
        for code in default_exceptions.keys():
            app.register_error_handler(code, handle_http_error)
        app.register_error_handler(AuthError, handle_auth_error)
        app.register_error_handler(ApiError, handle_api_error)
        app.register_error_handler(Exception, handle_exception)


def handle_http_error(error: HTTPException) -> Tuple[Response, int]:
    error.code = error.code or 500
    if error.code >= 500:
        current_app.logger.exception(error)
    return jsonify({
        'status': 'error',
        'message': str(error),
        'code': error.code,
        'errors': [
            error.description
        ]
    }), error.code


def handle_auth_error(error: AuthError) -> Tuple[Response, int,
                                                 Dict[str, Any]]:
    return jsonify({
        'status': 'error',
        'message': error.message,
        'code': error.code,
        'errors': error.errors
    }), error.code, {'WWW-Authenticate': 'Bearer realm=Turplanlegger'}


def handle_api_error(error: ApiError) -> Tuple[Response, int]:
    if error.code >= 500:
        current_app.logger.exception(error)
    return jsonify({
        'status': 'error',
        'message': error.message,
        'code': error.code,
        'errors': error.errors
    }), error.code


def handle_exception(error: Exception) -> Union[Tuple[Response, int],
                                                Exception]:
    # RoutingExceptions are used internally to trigger routing
    # actions, such as slash redirects raising RequestRedirect.
    if isinstance(error, RoutingException):
        return error

    current_app.logger.exception(error)
    return jsonify({
        'status': 'error',
        'message': str(error),
        'code': 500,
        'errors': [
            traceback.format_exc()
        ]
    }), 500
