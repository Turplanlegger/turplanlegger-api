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
            'notes': [note.serialize for note in self.notes],
            'routes': [route.serialize for route in self.routes],
            'item_lists': [list.serialize for list in self.item_lists],
            'create_time': self.create_time
        }

    def create(self) -> 'Trip':
        trip = self.get_trip(db.create_trip(self))
        if self.notes:
            notes = [Note(
                owner=trip.owner,
                content=note) for note in self.notes]
            notes = [item.create() for note in notes]
            trip.notes, self.notes = [notes, notes]

        if self.items_checked:
            items_checked = [ListItem(
                owner=item_list.owner,
                item_list=item_list.id,
                checked=True,
                content=item) for item in self.items_checked]
            items_checked = [item.create() for item in items_checked]
            item_list.items_checked, self.items_checked = [items_checked, items_checked]

        return item_list

    def delete(self) -> bool:
        return db.delete_route(self.id)

    @staticmethod
    def find_route(id: int) -> 'Route':
        return Route.get_route(db.get_route(id))

    def change_owner(self, owner: int) -> 'Route':
        if self.owner == owner:
            raise ValueError('new owner is same as old')

        # A user object should be parsed/passed
        # Return a boolean, don't get the list unless it's used
        return Route.get_route(db.change_route_owner(self.id, owner))

    @classmethod
    def get_route(cls, rec) -> 'Route':
        if isinstance(rec, dict):
            return Route(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                route=rec.get('route', None),
                route_history=rec.get('route_history', []),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return Route(
                id=rec.id,
                owner=rec.owner,
                route=rec.route,
                route_history=rec.route_history,
                create_time=rec.create_time
            )
