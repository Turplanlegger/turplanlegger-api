from flask import Blueprint, request

from turplanlegger.exceptions import ApiProblem

auth = Blueprint('auth', __name__)  # noqa isort:skip

from . import login  # noqa isort:skip


@auth.before_request
def before_request():
    if ((request.method in ['POST', 'PUT'] or (request.method == 'PATCH' and request.data))
            and not request.is_json):
        raise ApiProblem(
            'Request has wrong Content-Type',
            "PATCH, POST and PUT requests must set 'Content-type' to 'application/json'",
            415
        )
