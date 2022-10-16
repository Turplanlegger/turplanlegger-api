from datetime import datetime
from typing import Dict

from flask import g

from turplanlegger.app import db

JSON = Dict[str, any]


class Route:

    def __init__(self, owner: str, route: JSON, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field \'owner\'')
        if not isinstance(owner, str):
            raise TypeError('\'owner\' must be string')
        if not route:
            raise ValueError('Missing mandatory field \'route\'')

        self.owner = owner
        self.route = route
        self.id = kwargs.get('id', None)
        self.route_history = kwargs.get('route_history', [])
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'Route':
        return Route(
            id=json.get('id', None),
            owner=g.user.id,
            route=json.get('route', None),
            route_history=json.get('route_history', []),
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'owner': self.owner,
            'route': self.route,
            'route_history': self.route_history,
            'create_time': self.create_time
        }

    def create(self) -> 'Route':
        route = self.get_route(db.create_route(self.route, self.owner))
        return route

    def delete(self) -> bool:
        return db.delete_route(self.id)

    @staticmethod
    def find_route(id: int) -> 'Route':
        return Route.get_route(db.get_route(id))

    @staticmethod
    def find_routes_by_owner(owner_id: str) -> '[Route]':
        return [Route.get_route(route) for route in db.get_routes_by_owner(owner_id)]

    def change_owner(self, owner: str) -> 'Route':
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
