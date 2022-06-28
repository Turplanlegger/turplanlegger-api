from datetime import datetime
from typing import Dict

from turplanlegger.app import db
from turplanlegger.models.note import Note

JSON = Dict[str, any]


class Trip:

    def __init__(self, owner: int, name: str, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field \'owner\'')
        if not isinstance(owner, int):
            raise TypeError('\'owner\' must be integer')
        if not name:
            raise ValueError('Missing mandatory field \'name\'')
        if not isinstance(name, str):
            raise TypeError('\'name\' must be string')

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
        name = json.get('name', None)
        if len(name) > 512:
            raise ValueError("'name' is too long")

        return Trip(
            id=json.get('id', None),
            owner=json.get('owner', None),
            name=json.get('name', None),
            private=json.get('private', False)
        )

    @property
    def serialize(self) -> JSON:
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
        trip = self.get_trip(db.create_trip(self))
        return trip

    def delete(self) -> bool:
        return db.delete_trip(self.id)

    def addNoteReference(self, note_id: int) -> 'Trip':
        db.add_trip_note_reference(self.id, note_id)
        self.notes = db.get_trip_notes(self.id)

    def addRouteReference(self, route_id: int) -> 'Trip':
        db.add_trip_route_reference(self.id, route_id)
        self.routes = db.get_trip_routes(self.id)

    @staticmethod
    def find_trip(id: int) -> 'Trip':
        trip = Trip.get_trip(db.get_trip(id))
        return trip

    def change_owner(self, owner: int) -> 'Trip':
        if self.owner == owner:
            raise ValueError('new owner is same as old')

        # A user object should be parsed/passed
        # Return a boolean, don't get the list unless it's used
        return Trip.get_trip(db.change_trip_owner(self.id, owner))

    @classmethod
    def get_trip(cls, rec) -> 'Trip':
        if isinstance(rec, dict):
            trip = Trip(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                name=rec.get('name', None)
            )
            trip.notes = [item.note_id for item in db.get_trip_notes(trip.id)]
            trip.routes = [item.route_id for item in db.get_trip_routes(trip.id)]
            trip.item_lists = [item.item_list_id for item in db.get_trip_lists(trip.id)]
            return trip
        elif isinstance(rec, tuple):
            trip = Trip(
                id=rec.id,
                owner=rec.owner,
                name=rec.name
            )
            trip.notes = [item.note_id for item in db.get_trip_notes(trip.id)]
            trip.routes = [item.route_id for item in db.get_trip_routes(trip.id)]
            trip.item_lists = [item.item_list_id for item in db.get_trip_lists(trip.id)]
            return trip
