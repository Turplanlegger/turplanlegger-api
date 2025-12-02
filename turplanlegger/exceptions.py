import traceback
from typing import Any, Dict, Optional, Tuple, Union

from flask import Response, jsonify, request
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RoutingException

from turplanlegger.utils.logger import log


class ApiProblem(Exception):
    def __init__(
        self,
        title: Optional[str] = None,
        detail: Optional[str] = None,
        status: Optional[int] = None,
        type: Optional[str] = None,
        instance: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.title: str = title
        self.detail: Optional[str] = detail
        self.status: int = status or 500
        self.type: str = type or 'about:blank'
        self.instance: str = instance or request.url
        self.kwargs: Dict = kwargs


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
        app.register_error_handler(ApiProblem, handle_api_problem)
        app.register_error_handler(ApiError, handle_api_error)
        app.register_error_handler(Exception, handle_exception)


def handle_http_error(problem: HTTPException) -> Tuple[Response, int]:
    if problem.code >= 500:
        log.exception(problem)
    return (
        jsonify(
            {
                'type': f'https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/{problem.code}',
                'status': problem.code,
                'title': str(problem),
                'detail': problem.description,
                'instance': request.url,
            }
        ),
        problem.code,
        {'Content-Type': 'application/problem+json'},
    )


def handle_auth_error(error: AuthError) -> Tuple[Response, int, Dict[str, Any]]:
    return (
        jsonify({'status': 'error', 'message': error.message, 'code': error.code, 'errors': error.errors}),
        error.code,
        {'WWW-Authenticate': 'Bearer realm=Turplanlegger'},
    )


def handle_api_problem(problem: ApiProblem) -> Tuple[Response, int, Dict[str, Any]]:
    if problem.status >= 500:
        log.exception(problem)
    return (
        jsonify(
            {
                'type': problem.type,
                'status': problem.status,
                'title': problem.title,
                'detail': problem.detail,
                'instance': problem.instance,
            }
        ),
        problem.status,
        {'Content-Type': 'application/problem+json'},
    )


def handle_api_error(error: ApiError) -> Tuple[Response, int]:
    if error.code >= 500:
        log.exception(error)
    return jsonify(
        {'status': 'error', 'message': error.message, 'code': error.code, 'errors': error.errors}
    ), error.code


def handle_exception(error: Exception) -> Union[Tuple[Response, int], Exception]:
    # RoutingExceptions are used internally to trigger routing
    # actions, such as slash redirects raising RequestRedirect.
    if isinstance(error, RoutingException):
        return error

    log.exception(error)
    return jsonify({'status': 'error', 'message': str(error), 'code': 500, 'errors': [traceback.format_exc()]}), 500
