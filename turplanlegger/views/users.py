from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.user import User

from . import api


@api.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):

    user = User.find_user(user_id)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiError('user not found', 404)
