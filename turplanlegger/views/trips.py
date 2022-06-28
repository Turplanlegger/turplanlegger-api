from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.trip import Trip

from . import api


@api.route('/trip/<trip_id>', methods=['GET'])
def get_trip(trip_id):

    trip = Trip.find_trip(trip_id)
    if trip:
        return jsonify(status='ok', count=1, trip=trip.serialize)
    else:
        raise ApiError('route not found', 404)


@api.route('/trip', methods=['POST'])
def add_trip():
    try:
        trip = Trip.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        trip = trip.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(trip.serialize), 201

@api.route('/trip/note', methods=['PATCH'])
def add_note_to_trip():
    try:
        trip_id = request.json.get('trip_id', None)
        note_id = request.json.get('note_id', None)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        trip = Trip.find_trip(trip_id)
        trip.addNoteReference(note_id)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(trip.serialize), 201

@api.route('/trip/route', methods=['PATCH'])
def add_route_to_trip():
    try:
        trip_id = request.json.get('trip_id', None)
        route_id = request.json.get('route_id', None)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        trip = Trip.find_trip(trip_id)
        trip.addRouteReference(route_id)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(trip.serialize), 201

@api.route('/trip/item_list', methods=['PATCH'])
def add_item_list_to_trip():
    try:
        trip_id = request.json.get('trip_id', None)
        item_list_id = request.json.get('item_list_id', None)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        trip = Trip.find_trip(trip_id)
        trip.addItemListReference(item_list_id)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(trip.serialize), 201

@api.route('/trip/<trip_id>/owner', methods=['PATCH'])
def change_trip_owner(trip_id):

    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiError('trip not found', 404)

    owner = request.json.get('owner', None)
    if not owner:
        raise ApiError('must supply owner as int', 400)

    try:
        trip.change_owner(owner)
    except ValueError as e:
        raise ApiError(str(e), 400)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')