from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, NamedTuple
from uuid import UUID

from turplanlegger.app import db
from turplanlegger.models.access_level import AccessLevel

JSON = Dict[str, any]


class PermissionResult(Enum):
    ALLOWED = auto()
    NOT_FOUND = auto()
    INSUFFICIENT_PERMISSIONS = auto()


@dataclass
class Permission:
    object_id: int
    subject_id: UUID
    access_level: AccessLevel

    @classmethod
    def parse(cls, json: JSON) -> 'Permission':
        """Parse input JSON and return an Permission instance.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            An permission instance
        """

        return Permission(
            object_id=json.get('id', None),
            subject_id=json.get('subject_id', None),
            access_level=AccessLevel(json.get('access_level', None)),
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the Permission instance and returns it as Dict(str, any)"""
        return {'object_id': self.object_id, 'subject_id': self.subject_id, 'access_level': self.access_level}

    @staticmethod
    def find_trip_all_permissions(trip_id: int) -> 'Permission':
        return [Permission.get_permission(permission) for permission in db.get_trip_all_permissions(trip_id)]

    @staticmethod
    def find_trip_user_permissions(trip_id: int, user_id: UUID) -> 'Permission':
        return Permission.get_permission(db.get_trip_permissions(trip_id, user_id))

    def create(self) -> 'Permission':
        """Creates the Permission instance in the database"""
        return self.get_permission(db.create_trip_permissions(self))

    @classmethod
    def get_permission(cls, rec: NamedTuple) -> 'Permission':
        """Converts a database record to an Permission instance

        Args:
            rec (NamedTuple): Database record

        Returns:
            An Permission instance
        """
        if rec is None:
            return None

        return Permission(object_id=rec.trip_id, subject_id=rec.subject_id, access_level=rec.access_level)
