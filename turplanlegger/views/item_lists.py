from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.item_lists import ItemList
from turplanlegger.models.list_items import ListItem

from . import api


@api.route('/item_list/<item_list_id>', methods=['GET'])
@auth
def get_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if item_list:
        return jsonify(status='ok', count=1, item_list=item_list.serialize)
    else:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)


@api.route('/item_list/<item_list_id>', methods=['DELETE'])
@auth
def delete_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    try:
        item_list.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete item list', str(e), 500)

    return jsonify(status='ok')


@api.route('/item_list', methods=['POST'])
@auth
def add_item_list():
    try:
        item_list = ItemList.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem(title='Failed to parse item list', detail=str(e), status=400)

    try:
        item_list = item_list.create()
    except Exception as e:
        raise ApiProblem('Failed to create item list', str(e), 500)

    if item_list:
        return jsonify(status='ok', id=item_list.id, item_list=item_list.serialize), 201
    else:
        raise ApiProblem('Failed to create item list', 'Unknown error', 500)


@api.route('/item_list/<item_list_id>/add', methods=['PATCH'])
@auth
def add_item_list_items(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    items, items_checked = request.json.get('items', []), request.json.get('items_checked', [])
    if not items or not items_checked:
        raise ApiProblem('Item list empty', 'must supply items or items_checked to add as JSON list', 400)

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
        raise ApiProblem('Failed to parse items', str(e), 400)

    try:
        items = [item.create() for item in items]
        items_checked = [item.create() for item in items_checked]
    except Exception as e:
        raise ApiProblem('Failed to create item', str(e), 500)

    return jsonify(status='ok', count_items=len(items), count_items_checked=len(items_checked))


@api.route('/item_list/<item_list_id>/rename', methods=['PATCH'])
@auth
def rename_item_list(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    item_list.name = request.json.get('name', '')

    if item_list.rename():
        return jsonify(status='ok')
    else:
        raise ApiProblem('Failed to rename item list', 'Unknown error', 500)


@api.route('/item_list/<item_list_id>/toggle_check', methods=['PATCH'])
@auth
def toggle_list_item_check(item_list_id):

    if not request.json.get('items', []):
        raise ApiProblem('Failed to get items', 'Item(s) must be supplied as a JSON list', 400)

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    list_items = [item for item in item_list.items if item.id in request.json.get('items', [])]
    list_items_checked = [item for item in item_list.items_checked if item.id in request.json.get('items', [])]

    if not list_items and not list_items_checked:
        raise ApiProblem('Item not found in item list', f'An item was not found in item list id: {item_list.id}', 400)

    try:
        list_items = [item.toggle_check() for item in list_items]
        list_items_checked = [item.toggle_check() for item in list_items_checked]
    except Exception as e:
        raise ApiProblem('Failed to toggle item', str(e), 500)

    return jsonify(status='ok')


@api.route('/item_list/<item_list_id>/owner', methods=['PATCH'])
@auth
def change_item_list_owner(item_list_id):

    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiProblem('Owner is not int', 'Owner must be passed as an int', 400)

    try:
        item_list.change_owner(owner)
    except ValueError as e:
        raise ApiProblem('Failed to change owner of item list', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to change owner of item list', str(e), 500)

    return jsonify(status='ok')


@api.route('/item_list/mine', methods=['GET'])
@auth
def get_my_item_lists():

    item_lists = ItemList.find_item_list_by_owner(g.user.id)

    if item_lists:
        return jsonify(
            status='ok',
            count=len(item_lists),
            item_list=[item_list.serialize for item_list in item_lists]
        )
    else:
        raise ApiProblem(
            'Item lists not found',
            'No item lists were found for the requested user',
            404
        )
