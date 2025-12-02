from collections import namedtuple
from datetime import datetime
from typing import Dict, NamedTuple
from uuid import UUID

from flask import g

from turplanlegger.app import db
from turplanlegger.models.permission import Permission
from turplanlegger.models.trip_date import TripDate

JSON = Dict[str, any]
TRIP_DATE_UPDATE_STATUS = namedtuple('TRIP_DATE_UPDATE_STATUS', ['changed', 'errors'])


class Trip:
    """Trip object gathers TripDates, ItemLists with ListItems,
    Notes and Routes to plan a trip.

    The trip object can contain multiple ItemLists,
    Notes or Routes.

    Args:
        owner (UUID): The UUID4 of the owner of the object
        name (str): Name of the Trip.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        owner (UUID): The UUID4 of the owner of the object
        name (str): Name of the Trip
        id (int): Optional, the ID of the object
        private (bool): Flag if the trip is private
                        Default so False (public)
        dates (list): List if TripDates that are related to the trip
        notes (list): List of note ids that are related to the trip
        routes (list): List of route ids that are related to the trip
        item_list (list): List of item list ids that are related to
                          the trip
        permissions (list): List of permissions that are related to the trip
        create_time (datetime): Time of creation,
                                Default: datetime.now()
        update_time (datetime): Time of update

    """

    def __init__(self, owner: UUID, name: str, **kwargs) -> None:
        if not owner:
            raise ValueError("Missing mandatory field 'owner'")
        if not isinstance(owner, UUID):
            raise TypeError("'owner' must be UUID")
        if not name:
            raise ValueError("Missing mandatory field 'name'")
        if not isinstance(name, str):
            raise TypeError("'name' must be string")

        if name is not None and len(name) > 512:
            raise ValueError("'name' is too long")

        self.owner = owner
        self.name = name
        self.id = kwargs.get('id', None)
        self.private = kwargs.get('private', False)
        self.dates = kwargs.get('dates', [])
        self.notes = kwargs.get('notes', [])
        self.routes = kwargs.get('routes', [])
        self.item_lists = kwargs.get('item_lists', [])
        self.permissions = kwargs.get('permissions', None)
        self.create_time = kwargs.get('create_time', None) or datetime.now()
        self.update_time = kwargs.get('update_time', None)

    def __repr__(self):
        return (
            f"Trip(id='{self.id}', owner='{self.owner}', "
            f'private={self.private}, dates={self.dates}, '
            f'notes={self.notes}, routes={self.routes}, '
            f'item_lists={self.item_lists}, '
            f'create_time={self.create_time}, '
            f'permission={self.permissions})'
        )

    @classmethod
    def parse(cls, json: JSON) -> 'Trip':
        """Parse input JSON and return an Trip instance.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            An trip instance
        """

        dates = json.get('dates', [])
        if not isinstance(dates, list):
            raise TypeError('dates has to be a list of objects with start and end dates')
        dates[:] = [TripDate.parse(date) for date in dates]

        permissions = json.get('permissions', [])
        if not isinstance(permissions, list):
            raise TypeError('permissions has to be a list of permission objects')
        permissions[:] = [Permission.parse(permission) for permission in permissions]

        return Trip(
            owner=g.user.id,
            name=json.get('name', None),
            id=json.get('id', None),
            private=json.get('private', False),
            dates=dates,
            permissions=permissions,
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the Trip instance and returns it as Dict(str, any)"""
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'dates': [date.serialize for date in self.dates],
            'private': self.private,
            'notes': self.notes,
            'routes': self.routes,
            'item_lists': self.item_lists,
            'create_time': self.create_time.isoformat(),
            'permissions': [permission.serialize for permission in self.permissions],
        }

    def create(self) -> 'Trip':
        """Creates the Trip instance along with any trip_dates in the database"""
        trip = self.get_trip(db.create_trip(self))
        if self.dates:
            dates = []
            for date in self.dates:
                date.trip_id = trip.id
                dates.append(date.create())
            trip.dates = dates
        if self.permissions:
            permissions = []
            for permission in self.permissions:
                permission.object_id = trip.id
                permissions.append(permission.create_trip())
            trip.permissions = permissions
        return trip

    def delete(self) -> bool:
        """Deletes the Trip object from the database
        Returns True if deleted"""
        return db.delete_trip(self.id)

    def update(self, updated_fields) -> None:
        return db.update_trip(self, updated_fields)

    def add_note_reference(self, note_id: int) -> 'Trip':
        """Adds a note to the trip instance

        Args:
            note_id (int): Id of note

        Returns:
            dict of notes from the database
        """
        db.add_trip_note_reference(self.id, note_id)
        self.notes = db.get_trip_notes(self.id)

    def add_route_reference(self, route_id: int) -> 'Trip':
        """Adds a route to the trip instance

        Args:
            note_id (int): Id of note

        Returns:
            dict of routes from the database
        """
        db.add_trip_route_reference(self.id, route_id)
        self.routes = db.get_trip_routes(self.id)

    def add_item_list_reference(self, item_list_id: int) -> 'Trip':
        db.add_trip_item_list_reference(self.id, item_list_id)
        self.routes = db.get_trip_item_lists(self.id)

    @staticmethod
    def update_trip_dates(dates: JSON, trip: 'Trip') -> 'TRIP_DATE_UPDATE_STATUS':
        """Checks dates as JSON for updates in related Trip
        Dates will be updated troughout the function

        Args:
            dates (JSON): TripDates as JSON structure
            trip (Trip): Date related to dates

        Returns: TRIP_DATE_UPDATE_STATUS
        """
        errors = []
        dates_existing = []
        date_ids_existing = []
        trip_changed = False

        for date in dates:
            if date.get('id', None) is None:
                date['trip_id'] = trip.id
                try:
                    TripDate.parse(date).create(return_result=False)
                except (ValueError, KeyError) as e:
                    errors.append({'error': 'Failed to parse new date', 'object': date, 'details': e})
                else:
                    trip_changed = True

                continue

            try:
                dates_existing.append(TripDate.parse(date))
            except (ValueError, KeyError) as e:
                errors.append({'error': 'Failed to parse existing date', 'object': date, 'details': e})
            else:
                date_ids_existing.append(date.get('id', None))

        for date in trip.dates:
            if date.id not in date_ids_existing:
                try:
                    date.delete()
                except Exception as e:
                    errors.append({'error': 'Failed to delete existing date', 'object': date, 'details': e})
                else:
                    trip_changed = True

        for date_from_input in dates_existing:
            date_to_update = None
            for date_in_db in trip.dates:
                if date_in_db.id == date_from_input.id:
                    date_to_update = date_in_db
                    break

            date_changed = False
            if date_to_update is not None:
                for attribute, value in vars(date_to_update).items():
                    if attribute in ['id', 'trip_id', 'create_time']:
                        continue
                    if getattr(date_to_update, attribute, None) != getattr(date_from_input, attribute, None):
                        trip_changed = True
                        date_changed = True
                        setattr(date_to_update, attribute, getattr(date_from_input, attribute, None))

            if date_changed is True:
                try:
                    date_to_update.update()
                except Exception as e:
                    errors.append({'error': 'Failed to update existing date', 'object': date, 'details': e})
                else:
                    trip_changed = True

        return TRIP_DATE_UPDATE_STATUS(trip_changed, errors)

    @staticmethod
    def find_trip(trip_id: int) -> 'Trip':
        """Looks up an trip based on id

        Args:
            id (int): Id of Trip

        Returns:
            An Trip
        """
        return Trip.get_trip(db.get_trip(int(trip_id)))

    @staticmethod
    def find_trips_by_owner(owner_id: str) -> 'list[Trip]':
        """Looks up Trips by owner

        Args:
            owner_id (str): Id (uuid4) of owner

        Returns:
            A list of Trip istances
        """
        return [Trip.get_trip(trip) for trip in db.get_trips_by_owner(owner_id)]

    def change_owner(self, owner_id: UUID) -> bool:
        """Change owner of the Trip
        Won't change owner if new owner is the same as current

        Args:
            owner_id (UUID): id of the new owner

        Raises:
            ValueError if new owner is the same as old
            Exception from database

        Returns:
            The updated Trip object
        """
        if self.owner == owner_id:
            raise ValueError('new owner is same as old')

        db.change_trip_owner(self.id, owner_id)
        return True

    @classmethod
    def get_trip(cls, rec: NamedTuple) -> 'Trip':
        """Converts a database record to an Trip instance

        Args:
            rec (NamedTuple): Database record

        Returns:
            An Trip instance
        """
        if rec is None:
            return None

        trip = Trip(id=rec.id, owner=rec.owner, name=rec.name, private=rec.private, create_time=rec.create_time)
        trip.permissions = Permission.find_trip_all_permissions(trip.id)
        trip.dates = TripDate.find_by_trip_id(trip.id)
        trip.notes = [item.note_id for item in db.get_trip_notes(trip.id)]
        trip.routes = [item.route_id for item in db.get_trip_routes(trip.id)]
        trip.item_lists = [item.item_list_id for item in db.get_trip_item_lists(trip.id)]
        return trip
