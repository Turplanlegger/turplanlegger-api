from typing import Dict, NamedTuple

from flask import g

from turplanlegger.app import db

JSON = Dict[str, any]


class Trip:
    """Trip object gathers ItemLists with ListItems,
    Notes and Routes to plan a trip.

    The trip object can contain multiple ItemLists,
    Notes or Routes.

    Args:
        owner (str): The UUID4 of the owner of the object
        name (str): Name of the Trip.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        owner (str): The UUID4 of the owner of the object
        name (str): Name of the Trip
        id (int): Optional, the ID of the object
        private (bool): Flag if the trip is private
                        Default so False (public)
        create_time (datetime): Start time of the date
        create_time (datetime): End of the trip
        notes (list): List of note ids that are related to the trip
        routes (list): List of route ids that are related to the trip
        item_list (list): List of item list ids that are related to
                          the trip

    """

    def __init__(self, owner: str, name: str, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field \'owner\'')
        if not isinstance(owner, str):
            raise TypeError('\'owner\' must be string')
        if not name:
            raise ValueError('Missing mandatory field \'name\'')
        if not isinstance(name, str):
            raise TypeError('\'name\' must be string')

        if name is not None and len(name) > 512:
            raise ValueError("'name' is too long")

        self.owner = owner
        self.name = name
        self.id = kwargs.get('id', None)
        self.private = kwargs.get('private', False)
        self.create_time = kwargs.get('date_start', None)
        self.create_time = kwargs.get('date_end', None)
        self.notes = kwargs.get('notes', [])
        self.routes = kwargs.get('routes', [])
        self.item_lists = kwargs.get('item_lists', [])

    @classmethod
    def parse(cls, json: JSON) -> 'Trip':
        """Parse input JSON and return an Trip instance.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            An trip instance
        """

        return Trip(
            id=json.get('id', None),
            owner=g.user.id,
            name=json.get('name', None),
            private=json.get('private', False)
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the Trip instance and returns it as Dict(str, any)"""
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'notes': self.notes,
            'routes': self.routes,
            'item_lists': self.item_lists,
            'create_time': self.create_time
        }

    def create(self) -> 'Trip':
        """Creates the Trip instance in the database"""
        trip = self.get_trip(db.create_trip(self))
        return trip

    def delete(self) -> bool:
        """Deletes the Route object from the database
        Returns True if deleted"""
        return db.delete_trip(self.id)

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
    def find_trip(id: int) -> 'Trip':
        """Looks up an trip based on id

        Args:
            id (int): Id of Trip

        Returns:
            An Trip
        """
        return Trip.get_trip(db.get_trip(id))

    @staticmethod
    def find_trips_by_owner(owner_id: str) -> '[Trip]':
        """Looks up Trips by owner

        Args:
            owner_id (str): Id (uuid4) of owner

        Returns:
            A list of Trip istances
        """
        return [Trip.get_trip(trip) for trip in db.get_trips_by_owner(owner_id)]

    def change_owner(self, owner: str) -> 'Trip':
        """Change owner of the Trip
        Won't change name if new name is the same as current

        Args:
            owner (str): id (uuid4) of the new owner

        Returns:
            The updated Trip object
        """
        if self.owner == owner:
            raise ValueError('new owner is same as old')
        return Trip.get_trip(db.change_trip_owner(self.id, owner))

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

        trip = Trip(
            id=rec.id,
            owner=rec.owner,
            name=rec.name
        )
        trip.notes = [item.note_id for item in db.get_trip_notes(trip.id)]
        trip.routes = [item.route_id for item in db.get_trip_routes(trip.id)]
        trip.item_lists = [item.item_list_id for item in db.get_trip_item_lists(trip.id)]
        return trip
