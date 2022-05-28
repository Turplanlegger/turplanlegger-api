from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.item_lists import ItemList
from turplanlegger.models.list_items import ListItem

from . import api


@api.route('/item_list/<item_list_id>', methods=['GET'])
def get_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if item_list:
        return jsonify(status='ok', count=1, item_list=item_list.serialize)
    else:
        raise ApiError('not found', 404)


@api.route('/item_list/<item_list_id>', methods=['DELETE'])
def delete_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiError('item_list not found', 404)

    try:
        item_list.delete()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


@api.route('/item_list', methods=['POST'])
def add_item_list():
    try:
        item_list = ItemList.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        item_list = item_list.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    if item_list:
        return jsonify(status='ok', id=item_list.id, item_list=item_list.serialize), 201
    else:
        raise ApiError('Creation of item list failed', 500)


@api.route('/item_list/<item_list_id>/add', methods=['PATCH'])
def add_item_list_items(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiError('item_list not found', 404)

    items, items_checked = request.json.get('items', []), request.json.get('items_checked', [])
    if not items or not items_checked:
        raise ApiError('must supply items or items_checked to add as JSON list', 400)

    try:
        items = [
            ListItem.parse(
                {
                    'owner': item_list.owner,
                    'item_list': item_list.id,
                    'checked': False,
                    'content': item
                }
            ) for item in items
        ]
        items_checked = [
            ListItem.parse(
                {
                    'owner': item_list.owner,
                    'item_list': item_list.id,
                    'checked': True,
                    'content': item
                }
            ) for item in items_checked
        ]
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        items = [item.create() for item in items]
        items_checked = [item.create() for item in items_checked]
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok', count_items=len(items), count_items_checked=len(items_checked))


@api.route('/item_list/<item_list_id>/rename', methods=['PATCH'])
def rename_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiError('item list not found', 404)

    item_list.name = request.json.get('name', '')

    if item_list.rename():
        return jsonify(status='ok')
    else:
        raise ApiError('failed to rename item_list')


@api.route('/item_list/<item_list_id>/toggle_check', methods=['PATCH'])
def toggle_list_item_check(item_list_id):

    if not request.json.get('items', []):
        raise ApiError('must supply items as a JSON list', 400)

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiError('item list not found', 404)

    list_items = [item for item in item_list.items if item.id in request.json.get('items', [])]
    list_items_checked = [item for item in item_list.items_checked if item.id in request.json.get('items', [])]

    if not list_items and not list_items_checked:
        raise ApiError(f'items not found in item_list {item_list.id}', 400)

    try:
        list_items = [item.toggle_check() for item in list_items]
        list_items_checked = [item.toggle_check() for item in list_items_checked]
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


@api.route('/item_list/<item_list_id>/owner', methods=['PATCH'])
def change_item_list_owner(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiError('item list not found', 404)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiError('must supply owner as int', 400)

    try:
        item_list.change_owner(owner)
    except ValueError as e:
        raise ApiError(str(e), 400)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')
