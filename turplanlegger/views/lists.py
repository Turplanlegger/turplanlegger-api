from flask import current_app, g, jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.lists import List

from . import api


@api.route('/list/<list_id>', methods=['GET'])
def get_list(list_id):

    list = List.find_list(list_id)

    if list:
        return jsonify(status='ok', count=1, list=list.serialize)
    else:
        raise ApiError('not found', 404)


@api.route('/list', methods=['POST'])
def add_list():
    try:
        list = List.parse(request.json)
    except ValueError as e:
        raise ApiError(str(e), 400)

    try:
        list = list.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(list.serialize), 200


@api.route('/list/<list_id>/add', methods=['PATCH'])
def add_list_items(list_id):

    items = request.json.get('items')

    if not items:
        raise ApiError('must supply items to add as JSON list', 400)

    list = List.find_list(list_id)

    if not list:
        raise ApiError('list not found', 404)

    if list.add_list_items(items):
        return jsonify(status='ok')
    else:
        raise ApiError('failed to add items')
