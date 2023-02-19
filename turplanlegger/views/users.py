from flask import jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.user import User

from . import api


@api.route('/user/<user_id>', methods=['GET'])
@auth
def get_user(user_id):
    user = User.find_user(user_id)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiProblem('User not found', 'The requested user was not found', 404)


@api.route('/user', methods=['GET'])
@auth
def lookup_user():
    try:
        email = request.args.get('email', None)
    except KeyError as e:
        raise ApiProblem('Failed to get user', str(e), 400)

    if not email:
        raise ApiProblem('Failed to get user', 'Provide \'email\' in JSON body', 400)

    try:
        user = User.find_by_email(email)
    except ValueError as e:
        raise ApiProblem('Failed to get user', str(e), 400)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiProblem('User not found', 'The requested user was not found', 404)


@api.route('/user', methods=['POST'])
@auth
def add_user():
    try:
        user = User.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse user', str(e), 400)

    try:
        user = user.create()
    except Exception as e:
        raise ApiProblem('Failed to create user', str(e), 500)

    if user:
        return jsonify(status='ok', id=user.id, user=user.serialize), 201
    else:
        raise ApiProblem('Failed to create user', 'Unknown error', 500)


@api.route('/user/<user_id>', methods=['DELETE'])
@auth
def delete_user(user_id: str):
    user = User.find_user(user_id)

    if not user:
        raise ApiProblem('User not found', 'The requested user was not found', 404)

    try:
        user.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete user', str(e), 500)

    return jsonify(status='ok')


@api.route('/user/<user_id>/rename', methods=['PATCH'])
@auth
def rename_user(user_id: str):
    user = User.find_user(user_id)

    if not user:
        raise ApiProblem('User not found', 'The requested user was not found', 404)

    user.name = request.json.get('name', user.name)
    user.last_name = request.json.get('last_name', user.last_name)

    if user.rename():
        return jsonify(status='ok', id=user.id, user=user.serialize), 200
    else:
        raise ApiProblem('Failed to rename user', 'Unknown error', 500)


@api.route('/user/<user_id>/private', methods=['PATCH'])
@auth
def toggle_private_user(user_id: str):
    user = User.find_user(user_id)

    if not user:
        raise ApiProblem('User not found', 'The requested user was not found', 404)

    try:
        user.toggle_private()
    except Exception as e:
        raise ApiProblem('Failed to toggle users private setting', str(e), 500)

    return jsonify(status='ok')


@api.route('/whoami', methods=['GET'])
@auth
def lookup_self():

    user = User.find_user(g.user.id)

    if user:
        return jsonify(status='ok', count=1, user=user.serialize)
    else:
        raise ApiProblem('User not found', 'The requested user was not found', 404)