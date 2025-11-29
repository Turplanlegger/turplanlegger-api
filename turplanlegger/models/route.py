from datetime import datetime
from typing import Dict, NamedTuple
from uuid import UUID

from flask import g

from turplanlegger.app import db
from turplanlegger.models.permission import Permission

JSON = Dict[str, any]


class Route:
    """A route object. An object containing geometry
    to make up a route/path.

    Args:
        owner (UUID): The UUID4 of the owner of the object
        route (Dict[str, any]): JSON containing geometry
                                that makes up the path/route
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (int): Optional, the ID of the object
        owner (UUID): The UUID4 of the owner of the object
        comment (str): Optional route comment
        route (Dict[str, any]): JSON containing geometry
                                that makes up the path/route
        route_history (list): List of routes that makes up history
        permissions (list): List of permissions related to the route
        create_time (datetime): Time of creation,
                                Default: datetime.now()
    """

    def __init__(self, owner: UUID, route: JSON, **kwargs) -> None:
        if not owner:
            raise ValueError("Missing mandatory field 'owner'")
        if not isinstance(owner, UUID):
            raise TypeError("'owner' must be UUID")
        if not route:
            raise ValueError("Missing mandatory field 'route'")

        self.owner = owner
        self.route = route
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.comment = kwargs.get('comment', None)
        self.route_history = kwargs.get('route_history', [])
        self.permissions = kwargs.get('permissions', None)
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    def __repr__(self):
        return (
            f"Route(id='{self.id}', owner='{self.owner}', "
            f"name='{self.name}, comment='{self.comment}, "
            f'permissions={self.permissions}), '
            f'route={self.route}, route_history={self.route_history}, '
            f'create_time={self.create_time})'
        )

    @classmethod
    def parse(cls, json: JSON) -> 'Route':
        """Parse input JSON and return an Route object.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            A Route object
        """

        permissions = json.get('permissions', [])
        if not isinstance(permissions, list):
            raise TypeError('permissions has to be a list of permission objects')
        permissions[:] = [Permission.parse(permission) for permission in permissions]

        return Route(
            id=json.get('id', None),
            owner=g.user.id,
            route=json.get('route', None),
            route_history=json.get('route_history', []),
            name=json.get('name', None),
            comment=json.get('comment', None),
            permissions=permissions,
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the Route instance, returns it as Dict(str, any)"""
        return {
            'id': self.id,
            'owner': self.owner,
            'route': self.route,
            'route_history': self.route_history,
            'create_time': self.create_time,
            'name': self.name,
            'comment': self.comment,
            'permissions': [permission.serialize for permission in self.permissions],
        }

    def create(self) -> 'Route':
        """Creates the Route object in the database"""
        route = self.get_route(db.create_route(self.route, self.owner, self.name, self.comment))
        if self.permissions:
            permissions = []
            for permission in self.permissions:
                permission.object_id = route.id
                permissions.append(permission.create_route())
            route.permissions = permissions
        return route

    def delete(self) -> bool:
        """Deletes the Route object from the database
        Returns True if deleted"""
        return db.delete_route(self.id)

    @staticmethod
    def find_route(id: int) -> 'Route':
        """Looks up an Route based on id

        Args:
            id (int): Id of Route

        Returns:
            An Route
        """
        return Route.get_route(db.get_route(id))

    @staticmethod
    def find_routes_by_owner(owner_id: str) -> '[Route]':
        """Looks up Routes by owner

        Args:
            owner_id (str): Id (uuid4) of owner

        Returns:
            A list of Route objects
        """
        return [Route.get_route(route) for route in db.get_routes_by_owner(owner_id)]

    def change_owner(self, owner_id: UUID) -> bool:
        """Change owner of the Route
        Won't change name if new name is the same as current

        Args:
            owner (UUID): id of the new owner

        Raises:
            ValueError if new owner is the same as old
            Exception from database

        Returns:
            The updated Route object
        """
        if self.owner == owner_id:
            raise ValueError('new owner is same as old')

        try:
            db.change_route_owner(self.id, owner_id)
        except Exception:
            raise
        return True


    @staticmethod
    def add_permissions(permissions: tuple[Permission]) -> tuple[Permission]:
        return tuple(perm.create_route() for perm in permissions)

    @staticmethod
    def delete_permission(permission: Permission) -> None:
        return permission.delete_route()

    @staticmethod
    def update_permission(permission: Permission) -> None:
        return permission.update_route()

    @classmethod
    def get_route(cls, rec: NamedTuple) -> 'Route':
        """Converts a database record to an Route object

        Args:
            rec (NamedTuple): Database record

        Returns:
            An Route object
        """
        if rec is None:
            return None

        return Route(
            id=rec.id,
            owner=rec.owner,
            route=rec.route,
            route_history=rec.route_history,
            permissions=Permission.find_route_all_permissions(rec.id),
            name=rec.name,
            comment=rec.comment,
            create_time=rec.create_time,
        )
