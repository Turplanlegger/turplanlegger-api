from uuid import UUID
from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.access_level import AccessLevel
from turplanlegger.models.permission import Permission, PermissionResult
from turplanlegger.models.route import Route

from . import api


@api.route('/routes/<route_id>', methods=['GET'])
@auth
def get_route(route_id):
    route = Route.find_route(route_id)
    if (
        route
        and Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ) is PermissionResult.ALLOWED
    ):
        return jsonify(status='ok', count=1, route=route.serialize)
    else:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)


@api.route('/routes/<route_id>', methods=['DELETE'])
@auth
def delete_route(route_id):
    route = Route.find_route(route_id)

    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    perms = Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.DELETE)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to delete the route', 403)

    try:
        route.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete route', str(e), 500)

    return jsonify(status='ok')


@api.route('/routes', methods=['POST'])
@auth
def add_route():
    try:
        route = Route.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse route', str(e), 400)

    try:
        route = route.create()
    except Exception as e:
        raise ApiProblem('Failed to create route', str(e), 500)

    return jsonify(route.serialize), 201


@api.route('/routes/<route_id>/owner', methods=['PATCH'])
@auth
def change_route_owner(route_id):
    route = Route.find_route(route_id)

    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    perms = Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    if route.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change owner the route', 403)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiProblem('Owner is not int', 'Owner must be passed as an int', 400)

    try:
        route.change_owner(owner)
    except ValueError as e:
        raise ApiProblem('Failed to change owner of route', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to change owner of route', str(e), 500)

    return jsonify(status='ok')


@api.route('/routes/mine', methods=['GET'])
@auth
def get_my_routes():
    routes = Route.find_routes_by_owner(g.user.id)

    if routes:
        return jsonify(status='ok', count=len(routes), route=[route.serialize for route in routes])
    else:
        raise ApiProblem('route not found', 'No routes were found for the requested user', 404)


@api.route('/routes/<route_id>/permissions', methods=['PATCH'])
@auth
def add_route_permissions(route_id):
    route = Route.find_route(route_id)
    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    perms = Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    if route.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to add route permissions', 403)

    permissions_input = request.json.get('permissions', [])

    if not isinstance(permissions_input, list) or not permissions_input:
        raise ApiProblem('Bad Request', 'You must supply a non-empty "permissions" array', 400)

    new_permissions = []
    for perm in permissions_input:
        if perm.get('object_id', None) is None:
            perm['object_id'] = route.id
            new_permissions.append(perm)
            continue
        if perm.get('object_id', None) != route.id:
            continue

    try:
        permissions = tuple(Permission.parse(permission) for permission in new_permissions)
    except ValueError:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)

    for perm in permissions:
        if perm in route.permissions:
            raise ApiProblem('Failed to add permissions', 'The permission already exists', 409)

    try:
        new_permissions = route.add_permissions(permissions)
    except ValueError as e:
        raise ApiProblem('Failed to add new permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to add new permissions', str(e), 500)

    if len(new_permissions) > 0:
        return jsonify(status='ok', permissions=tuple(perm.serialize for perm in new_permissions))
    else:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)


@api.route('/routes/<route_id>/permissions/<user_id>', methods=['DELETE'])
@auth
def delete_route_permissions(route_id, user_id):
    route = Route.find_route(route_id)
    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    perms = Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    user_id = UUID(user_id)

    if g.user.id != user_id and route.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to remove route permissions', 403)

    permission = next((perm for perm in route.permissions if perm.subject_id == user_id), None)

    if permission is None:
        raise ApiProblem('Failed to delete permissions', 'User not found in permissions', 400)

    try:
        route.delete_permission(permission)
    except ValueError as e:
        raise ApiProblem('Failed to delete permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to delete permissions', str(e), 500)

    return ('', 204)


@api.route('/route/<route_id>/permissions/<user_id>', methods=['PATCH'])
@auth
def change_route_permissions(route_id, user_id):
    route = Route.find_route(route_id)
    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    perms = Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    if route.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change permissions', 403)

    user_id = UUID(user_id)
    permission = next((perm for perm in route.permissions if perm.subject_id == user_id), None)
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
        permission = route.update_permission(permission)
    except ValueError as e:
        raise ApiProblem('Failed to update permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to update permissions', str(e), 500)

    return jsonify(status='ok', permission=permission.serialize)
