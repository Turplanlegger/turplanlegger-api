from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.route import Route

from . import api


@api.route('/route/<route_id>', methods=['GET'])
def get_route(route_id):

    route = Route.find_route(route_id)

    if route:
        return jsonify(status='ok', count=1, route=route.serialize)
    else:
        raise ApiError('not found', 404)


@api.route('/route/<route_id>', methods=['DELETE'])
def delete_route(route_id):

    route = Route.find_route(route_id)

    if not route:
        raise ApiError('route not found', 404)

    try:
        route.delete()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


@api.route('/route', methods=['POST'])
def add_route():
    try:
        route = Route.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        route = route.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(route.serialize)


@api.route('/route/<route_id>/owner', methods=['PATCH'])
def change_route_owner(route_id):

    route = Route.find_route(route_id)

    if not route:
        raise ApiError('route list not found', 404)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiError('must supply owner as int', 400)

    try:
        route.change_owner(owner)
    except ValueError as e:
        raise ApiError(str(e), 400)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')
