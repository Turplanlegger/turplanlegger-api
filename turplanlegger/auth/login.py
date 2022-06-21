import re
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from uuid import uuid4

from turplanlegger.exceptions import ApiError
from turplanlegger.models.token import JWT


from . import auth, utils  # noqa isort:skip


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

    if not user:
        raise ApiError('Could not authorize user', 401)

    now = datetime.utcnow()
    token = JWT(
        iss=request.url_root,
        sub=user.id,
        aud='/',
        exp=(now + timedelta(seconds=current_app.config['TOKEN_EXPIRE_TIME'])),
        nbf=now,
        iat=now,
        jti=str(uuid4()),
        typ='JWT',
    )
    return jsonify(token=token.tokenize())
