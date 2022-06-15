import re
from flask import request, jsonify

from turplanlegger.exceptions import ApiError


from . import auth  # noqa isort:skip


@auth.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
    except KeyError:
        raise ApiError('Supply email and password', 401)

    p = re.compile('^[\\w.-]+@[\\w.-]+\\.\\w+$')
    if not p.match(email):
        raise ApiError('invalid email address', 401)

    from turplanlegger.models.user import User
    user = User.check_credentials(email, password)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiError('Could not authorize user', 401)
