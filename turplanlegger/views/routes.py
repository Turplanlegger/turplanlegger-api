from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.route import Route

from . import api


@api.route('/route/<route_id>', methods=['GET'])
@auth
def get_route(route_id):

    route = Route.find_route(route_id)

    if route:
        return jsonify(status='ok', count=1, route=route.serialize)
    else:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)


@api.route('/route/<route_id>', methods=['DELETE'])
@auth
def delete_route(route_id):

    route = Route.find_route(route_id)

    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

    try:
        route.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete route', str(e), 500)

    return jsonify(status='ok')


@api.route('/route', methods=['POST'])
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


@api.route('/route/<route_id>/owner', methods=['PATCH'])
@auth
def change_route_owner(route_id):

    route = Route.find_route(route_id)

    if not route:
        raise ApiProblem('Route not found', 'The requested route was not found', 404)

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
        return jsonify(
            status='ok',
            count=len(routes),
            route=[route.serialize for route in routes]
        )
    else:
        raise ApiProblem(
            'route not found',
            'No routes were found for the requested user',
            404
        )
