from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.access_level import AccessLevel
from turplanlegger.models.item_lists import ItemList
from turplanlegger.models.note import Note
from turplanlegger.models.permission import Permission, PermissionResult
from turplanlegger.models.route import Route
from turplanlegger.models.trip import Trip
from turplanlegger.models.trip_date import TripDate

from . import api


@api.route('/trips/<trip_id>', methods=['GET'])
@auth
def get_trip(trip_id):
    trip = Trip.find_trip(trip_id)
    if trip and (
        trip.private is False
        or Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.READ) is PermissionResult.ALLOWED
    ):
        return jsonify(status='ok', count=1, trip=trip.serialize)
    else:
        raise ApiProblem('Trip not found', 'The requested trip was not found', 404)


@api.route('/trips', methods=['POST'])
@auth
def add_trip():
    try:
        trip = Trip.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse trip', str(e), 400)
    try:
        trip = trip.create()
    except Exception as e:
        raise ApiProblem('Failed to create trip', str(e), 500)

    return jsonify(trip.serialize), 201


@api.route('/trips/<trip_id>', methods=['PUT'])
@auth
def update_trip(trip_id):
    trip = Trip.find_trip(trip_id)

    if not trip:
        raise ApiProblem('Trip not found', 'The requested trip was not found', 404)

    perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.MODIFY)
    if perms is PermissionResult.NOT_FOUND:
        if trip.private is True:
            raise ApiProblem('Trip not found', 'The requested trip was not found', 404)
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)

    errors = []
    trip_changed = False

    dates = request.json.get('dates', None)

    if dates is not None:
        date_status = Trip.update_trip_dates(dates, trip)
        if date_status.changed is True:
            trip_changed = True
        errors.extend(date_status.errors)

    name = request.json.get('name', trip.name)
    private = request.json.get('private', trip.private)
    updated_fields = []
    if name != trip.name:
        updated_fields.append('name')
    trip.name = name
    if private != trip.private:
        updated_fields.append('private')
    trip.private = private

    if len(updated_fields) > 0:
        try:
            trip.update(updated_fields)
        except Exception as e:
            errors.append({'error': 'Failed to update trip', 'object': trip, 'details': e})
        else:
            trip_changed = True

    if trip_changed is False:
        raise ApiProblem('Failed to update note', 'No new updates were written', 409)

    trip = Trip.find_trip(trip.id)

    return jsonify(status='ok', count=1, trip=trip.serialize, errors=errors)


@api.route('/trips/<trip_id>/notes', methods=['PATCH'])
@auth
def add_note_to_trip(trip_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to add note to trip', 'Trip was not found', 404)

    perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.MODIFY)
    if perms is PermissionResult.NOT_FOUND:
        if trip.private is True:
            raise ApiProblem('Trip not found', 'The requested trip was not found', 404)
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)

    note = Note.find_note(request.json.get('note_id', None))
    if not note:
        raise ApiProblem('Failed to add note to trip', 'Note was not found', 404)

    if Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ) is PermissionResult.NOT_FOUND:
        raise ApiProblem('Failed to add note to trip', 'Note was not found', 404)

    # I'm lazy, so I'm keeping this here until I fix private attribute for Note
    # if note.private is True:
    #     note_perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ)
    #     if note_perms is PermissionResult.NOT_FOUND:
    #         raise ApiProblem('Failed to add note to trip', 'Note was not found', 404)

    try:
        trip.add_note_reference(note.id)
    except Exception as e:
        raise ApiProblem('Failed to add note to trip', str(e), 500)

    return jsonify(trip.serialize), 201


@api.route('/trips/<trip_id>/routes', methods=['PATCH'])
@auth
def add_route_to_trip(trip_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to add note to trip', 'Trip was not found', 404)

    perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.MODIFY)
    if perms is PermissionResult.NOT_FOUND:
        if trip.private is True:
            raise ApiProblem('Trip not found', 'The requested trip was not found', 404)
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)

    route = Route.find_route(request.json.get('route_id', None))
    if not route:
        raise ApiProblem('Failed to add route to trip', 'Route was not found', 404)

    if Permission.verify(route.owner, route.permissions, g.user.id, AccessLevel.READ) is PermissionResult.NOT_FOUND:
        raise ApiProblem('Failed to add route to trip', 'Route was not found', 404)

    try:
        trip.add_route_reference(route.id)
    except Exception as e:
        raise ApiProblem('Failed to add route to trip', str(e), 500)

    return jsonify(trip.serialize), 201


@api.route('/trips/<trip_id>/item_lists', methods=['PATCH'])
@auth
def add_item_list_to_trip(trip_id):
    trip = Trip.find_trip(request.json.get('trip_id', None))
    if not trip:
        raise ApiProblem('Failed to add item list to trip', 'Trip was not found', 404)

    item_list = ItemList.find_item_list(request.json.get('item_list_id', None))
    if not item_list:
        raise ApiProblem('Failed to add item list to trip', 'Item list was not found', 404)

    if Permission.verify(item_list.owner, item_list.permissions, g.user.id, AccessLevel.READ) is PermissionResult.NOT_FOUND:
        raise ApiProblem('Failed to add item list to trip', 'Item list was not found', 404)
    try:
        trip.add_item_list_reference(item_list.id)
    except Exception as e:
        raise ApiProblem('Failed to add item list to trip', str(e), 500)

    return jsonify(trip.serialize), 201


@api.route('/trips/<trip_id>/owner', methods=['PATCH'])
@auth
def change_trip_owner(trip_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to change owner of trip', 'The requested trip was not found', 404)

    if g.user.id != trip.owner:
        perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.MODIFY)
        if trip.private is True and perms is PermissionResult.NOT_FOUND:
            raise ApiProblem('Failed to change owner of trip', 'The requested trip was not found', 404)
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change ownership the trip', 403)

    owner = request.json.get('owner', None)
    if not owner:
        raise ApiProblem('Failed to change owner', 'The requested owner was not found', 404)

    try:
        trip.change_owner(owner)
    except ValueError as e:
        raise ApiProblem('Failed to change owner', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to change owner', str(e), 500)

    return jsonify(status='ok')


@api.route('/trips/mine', methods=['GET'])
@auth
def get_my_trips():
    trips = Trip.find_trips_by_owner(g.user.id)

    if trips:
        return jsonify(status='ok', count=len(trips), trip=[trip.serialize for trip in trips])
    else:
        raise ApiProblem('Trip not found', 'No trips were found for the requested user', 404)


@api.route('/trips/<trip_id>', methods=['DELETE'])
@auth
def delete_trip(trip_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to delete trip', 'The requested trip was not found', 404)

    perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.DELETE)
    if perms is PermissionResult.NOT_FOUND:
        if trip.private is True:
            raise ApiProblem('Trip not found', 'The requested trip was not found', 404)
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)
    elif perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the trip', 403)

    try:
        trip.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete trip', str(e), 500)

    return jsonify(status='ok')


@api.route('/trips/<trip_id>/dates', methods=['PATCH'])
@auth
def add_trip_date(trip_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to add date to trip', 'The requested trip was not found', 404)

    request.json['trip_id'] = trip_id

    try:
        trip_date = TripDate.parse(request.json)
    except (ValueError, TypeError):
        raise ApiProblem('Failed to add date to trip', 'Parsing of the date failed', 400)

    try:
        trip_date = trip_date.create()
    except Exception as e:
        raise ApiProblem('Failed to add date to trip', str(e), 500)

    return jsonify(trip_date.serialize), 201


@api.route('/trips/<trip_id>/dates/<trip_date_id>', methods=['delete'])
@auth
def remove_trip_date(trip_id, trip_date_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to remove date from trip', 'The requested trip was not found', 404)

    perms = Permission.verify(trip.owner, trip.permissions, g.user.id, AccessLevel.DELETE)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Trip not found', 'The requested trip was not found', 404)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to delete the trip', 403)

    trip_date = None
    for date in trip.dates:
        if date.id == int(trip_date_id):
            trip_date = date
            break

    if trip_date is None:
        raise ApiProblem('Failed to remove date from trip', 'The requested date was not found in this trip', 404)

    try:
        trip_date.delete()
    except Exception:
        raise ApiProblem('Failed to remove date from trip', 'Failed to delete date', 404)

    return jsonify(status='ok')


@api.route('/trips/<trip_id>/dates/<trip_date_id>/select', methods=['patch'])
@auth
def select_trip_Date(trip_id, trip_date_id):
    trip = Trip.find_trip(trip_id)
    if not trip:
        raise ApiProblem('Failed to select trip date', 'The requested trip was not found', 404)

    trip_date = None
    for date in trip.dates:
        if date.id == int(trip_date_id):
            trip_date = date
            break

    if trip_date is None:
        raise ApiProblem('Failed to select trip date', 'The requested date was not found in this trip', 404)

    try:
        TripDate.unselect_by_trip_id(trip.id)
    except Exception:
        raise ApiProblem('Failed to select trip date', 'Failed to unselect dates for the trip', 500)

    try:
        trip_date.select()
    except Exception:
        raise ApiProblem('Failed to select trip date', 'Unkown error', 500)

    return jsonify(status='ok')
