from uuid import UUID

from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.access_level import AccessLevel
from turplanlegger.models.item_lists import ItemList
from turplanlegger.models.list_items import ListItem
from turplanlegger.models.permission import Permission, PermissionResult
from turplanlegger.models.user import User

from . import api


@api.route('/item_lists/<item_list_id>', methods=['GET'])
@auth
def get_item_list(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)

    if item_list and (
        item_list.private is False
        or Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ)
        is PermissionResult.ALLOWED
    ):
        return jsonify(status='ok', count=1, item_list=item_list.serialize)
    else:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)


@api.route('/item_lists/<item_list_id>', methods=['DELETE'])
@auth
def delete_item_list(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.DELETE)
    if item_list.private is False:
        if perms is not PermissionResult.ALLOWED:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to delete the item list', 403)
    else:
        if perms is PermissionResult.NOT_FOUND:
            raise ApiProblem('Item list not found', 'The requested item list was not found', 404)
        if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to delete the item list', 403)

    try:
        item_list.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete item list', str(e), 500)

    return jsonify(status='ok')


@api.route('/item_lists', methods=['POST'])
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


@api.route('/item_lists/<item_list_id>/add', methods=['PATCH'])
@auth
def add_item_list_items(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.MODIFY)
    if item_list.private is False:
        if perms is not PermissionResult.ALLOWED:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)
    else:
        if perms is PermissionResult.NOT_FOUND:
            raise ApiProblem('Item list not found', 'The requested item list was not found', 404)
        if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)

    items, items_checked = request.json.get('items', []), request.json.get('items_checked', [])
    if not items or not items_checked:
        raise ApiProblem('Item list empty', 'must supply items or items_checked to add as JSON list', 400)

    try:
        items = tuple(
            ListItem.parse(
                {'owner': g.user.id, 'item_list': item_list.id, 'checked': False, 'content': item.get('content')}
            )
            for item in items
        )
        items_checked = tuple(
            ListItem.parse(
                {'owner': g.user.id, 'item_list': item_list.id, 'checked': True, 'content': item.get('content')}
            )
            for item in items_checked
        )
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse items', str(e), 400)
    except Exception:
        # We should log this
        raise ApiProblem('Failed to parse items', 'Unknown error', 500)

    try:
        items = tuple(item.create() for item in items)
        items_checked = tuple(item.create() for item in items_checked)
    except Exception as e:
        raise ApiProblem('Failed to create item', str(e), 500)

    return jsonify(status='ok', count_items=len(items), count_items_checked=len(items_checked))


@api.route('/item_lists/<item_list_id>/rename', methods=['PATCH'])
@auth
def rename_item_list(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.MODIFY)
    if item_list.private is False:
        if perms is not PermissionResult.ALLOWED:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)
    else:
        if perms is PermissionResult.NOT_FOUND:
            raise ApiProblem('Item list not found', 'The requested item list was not found', 404)
        if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)

    item_list.name = request.json.get('name', '')

    if item_list.rename():
        return jsonify(status='ok')
    else:
        raise ApiProblem('Failed to rename item list', 'Unknown error', 500)


@api.route('/item_lists/<item_list_id>/toggle_check', methods=['PATCH'])
@auth
def toggle_list_item_check(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)
    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.MODIFY)
    if item_list.private is False:
        if perms is not PermissionResult.ALLOWED:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)
    else:
        if perms is PermissionResult.NOT_FOUND:
            raise ApiProblem('Item list not found', 'The requested item list was not found', 404)
        if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
            raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the item list', 403)

    if not request.json.get('toggle_items', []):
        raise ApiProblem(
            'Failed to get items', "Item(s) IDs must be supplied as a JSON list of ints in the key 'toggle_items'", 400
        )

    toggle_items = tuple(item for item in item_list.items if item.id in request.json.get('toggle_items', [])) + tuple(
        item for item in item_list.items_checked if item.id in request.json.get('toggle_items', [])
    )

    if not toggle_items:
        raise ApiProblem('Failed to toggle item lisitems', 'No items were successfully parsed', 400)

    try:
        tuple(item.toggle_check() for item in toggle_items)
    except Exception as e:
        raise ApiProblem('Failed to toggle item', str(e), 500)

    return jsonify(status='ok')


@api.route('/item_lists/<item_list_id>/owner', methods=['PATCH'])
@auth
def change_item_list_owner(item_list_id: int):
    item_list = ItemList.find_item_list(item_list_id)

    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ)
    if item_list.private is True and perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    if item_list.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change owner of the item list', 403)

    try:
        owner_id = UUID(request.json.get('owner', None))
    except (ValueError, TypeError):
        raise ApiProblem('Failed to change owner', 'Owner id must be passed as an UUID', 400)

    owner = User.find_user(owner_id)

    if not owner:
        raise ApiProblem('Failed to change owner', 'Requested owner not found', 404)

    try:
        item_list.change_owner(owner.id)
    except ValueError as e:
        raise ApiProblem('Failed to change owner of item list', str(e), 400)
    except Exception:
        raise ApiProblem('Failed to change owner of item list', 'Unknown error', 500)

    return ('', 204)


@api.route('/item_lists/mine', methods=['GET'])
@auth
def get_my_item_lists():
    item_lists = ItemList.find_item_list_by_owner(g.user.id)

    if item_lists:
        return jsonify(status='ok', count=len(item_lists), item_list=[item_list.serialize for item_list in item_lists])
    else:
        raise ApiProblem('Item lists not found', 'No item lists were found for the requested user', 404)


@api.route('/item_lists/public', methods=['GET'])
@auth
def get_public_item_lists():
    item_lists = ItemList.find_public_item_lists()

    if item_lists:
        return jsonify(status='ok', count=len(item_lists), item_list=[item_list.serialize for item_list in item_lists])
    else:
        raise ApiProblem('Item lists not found', 'No public item lists were found', 404)


@api.route('/item_lists/<item_list_id>/permissions', methods=['PATCH'])
@auth
def add_item_list_permissions(item_list_id):
    item_list = ItemList.find_item_list(item_list_id)
    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ)
    if item_list.private is True and perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested item_list was not found', 404)

    if item_list.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to add item list permissions', 403)

    permissions_input = request.json.get('permissions', [])

    if not isinstance(permissions_input, list) or not permissions_input:
        raise ApiProblem('Bad Request', 'You must supply a non-empty "permissions" array', 400)

    new_permissions = []
    for perm in permissions_input:
        if perm.get('object_id', None) is None:
            perm['object_id'] = item_list.id
            new_permissions.append(perm)
            continue
        if perm.get('object_id', None) != item_list.id:
            continue

    try:
        permissions = tuple(Permission.parse(permission) for permission in new_permissions)
    except ValueError:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)

    for perm in permissions:
        if perm in item_list.permissions:
            raise ApiProblem('Failed to add permissions', 'The permission already exists', 409)

    try:
        new_permissions = item_list.add_permissions(permissions)
    except ValueError as e:
        raise ApiProblem('Failed to add new permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to add new permissions', str(e), 500)

    if len(new_permissions) > 0:
        return jsonify(status='ok', permissions=tuple(perm.serialize for perm in new_permissions))
    else:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)


@api.route('/item_lists/<item_list_id>/permissions/<user_id>', methods=['DELETE'])
@auth
def delete_item_list_permissions(item_list_id, user_id):
    item_list = ItemList.find_item_list(item_list_id)
    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    user_id = UUID(user_id)

    if g.user.id != user_id and item_list.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to remove item list permissions', 403)

    permission = next((perm for perm in item_list.permissions if perm.subject_id == user_id), None)

    if permission is None:
        raise ApiProblem('Failed to delete permissions', 'User not found in permissions', 400)

    try:
        item_list.delete_permission(permission)
    except ValueError as e:
        raise ApiProblem('Failed to delete permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to delete permissions', str(e), 500)

    return ('', 204)


@api.route('/item_lists/<item_list_id>/permissions/<user_id>', methods=['PATCH'])
@auth
def change_item_list_permissions(item_list_id, user_id):
    item_list = ItemList.find_item_list(item_list_id)
    if not item_list:
        raise ApiProblem('Item list not found', 'The requested item_list was not found', 404)

    perms = Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ)
    if item_list.private is True and perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Item list not found', 'The requested item list was not found', 404)

    if item_list.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change permissions', 403)

    user_id = UUID(user_id)
    permission = next((perm for perm in item_list.permissions if perm.subject_id == user_id), None)
    if permission is None:
        raise ApiProblem('Failed to update permissions', 'User not found in permissions', 400)

    access_level_in = request.json.get('access_level', None)

    if access_level_in is None:
        raise ApiProblem('Bad Request', 'You must supply access_level as an string', 400)
    try:
        access_level = AccessLevel(access_level_in)
    except ValueError:
        raise ApiProblem('Failed to update permissions', 'Ensure access level is one of READ, MODIFY, OR DELETE', 400)

    permission.access_level = access_level

    try:
        permission = item_list.update_permission(permission)
    except ValueError as e:
        raise ApiProblem('Failed to update permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to update permissions', str(e), 500)

    return jsonify(status='ok', permission=permission.serialize)
