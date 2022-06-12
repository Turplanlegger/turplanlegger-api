from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.user import User

from . import api


@api.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):

    try:
        id = int(user_id)
    except ValueError:
        raise ApiError(f'\'{user_id}\' is not int', 400)

    user = User.find_user(id)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiError('user not found', 404)


@api.route('/user', methods=['POST'])
def add_user():
    try:
        user = User.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        user = user.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    if user:
        return jsonify(status='ok', id=user.id, user=user.serialize), 201
    else:
        raise ApiError('Creation of user failed', 500)


@api.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):

    try:
        id = int(user_id)
    except ValueError:
        raise ApiError(f'\'{user_id}\' is not int', 400)

    user = User.find_user(id)

    if not user:
        raise ApiError('user not found', 404)

    try:
        user.delete()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


@api.route('/user/<user_id>/rename', methods=['PATCH'])
def rename_user(user_id):

    try:
        id = int(user_id)
    except ValueError:
        raise ApiError(f'\'{user_id}\' is not int', 400)

    user = User.find_user(id)

    if not user:
        raise ApiError('item list not found', 404)

    user.name = request.json.get('name', user.name)
    user.last_name = request.json.get('last_name', user.last_name)

    if user.rename():
        return jsonify(status='ok', id=user.id, user=user.serialize), 200
    else:
        raise ApiError('Failed to rename user', 500)


@api.route('/user/<user_id>/private', methods=['PATCH'])
def toggle_private_user(user_id):

    try:
        id = int(user_id)
    except ValueError:
        raise ApiError(f'\'{user_id}\' is not int', 400)

    user = User.find_user(id)

    if not user:
        raise ApiError('item list not found', 404)

    try:
        user.toggle_private()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')
