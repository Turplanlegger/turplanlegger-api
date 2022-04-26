from flask import current_app, g, jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.list_item import ListItem
from turplanlegger.models.lists import List

from . import api


@api.route('/list/<list_id>', methods=['GET'])
def get_list(list_id):

    list = List.find_list(list_id)

    if list:
        return jsonify(status='ok', count=1, list=list.serialize)
    else:
        raise ApiError('not found', 404)


@api.route('/list/<list_id>', methods=['DELETE'])
def delete_list(list_id):

    list = List.find_list(list_id)

    if not list:
        raise ApiError('list not found', 404)

    try:
        list = list.delete()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


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

    return jsonify(list.serialize)


@api.route('/list/<list_id>/add', methods=['PATCH'])  # Consider using PUT instead of delete
def add_list_items(list_id):

    list = List.find_list(list_id)

    if not list:
        raise ApiError('list not found', 404)

    items, items_checked = request.json.get('items', []), request.json.get('items_checked', [])
    try:
        items = [ListItem(
            owner=list.owner,
            list=list.id,
            checked=False,
            content=item) for item in items]
        items_checked = [ListItem(
            owner=list.owner,
            list=list.id,
            checked=True,
            content=item) for item in items_checked]
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    if not items or not items_checked:
        raise ApiError('must supply items or items_checked to add as JSON list', 400)

    try:
        items = [item.create() for item in items]
        items_checked = [item.create() for item in items_checked]
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok', count_items=len(items), count_items_checked=len(items_checked))


@api.route('/list/<list_id>/rename', methods=['PATCH'])
def rename_list(list_id):

    list = List.find_list(list_id)

    if not list:
        raise ApiError('list not found', 404)

    list.name = request.json.get('name', '')

    if list.rename():
        return jsonify(status='ok')
    else:
        raise ApiError('failed to rename list')
