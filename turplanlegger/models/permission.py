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
            object_id=json.get('object_id', None),
            subject_id=UUID(json.get('subject_id', None)),
            access_level=AccessLevel(json.get('access_level', None)),
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the Permission instance and returns it as Dict(str, any)"""
        return {'object_id': self.object_id, 'subject_id': self.subject_id, 'access_level': self.access_level}

    @staticmethod
    def verify(
        owner: UUID, permissions: list['Permission'], subject_id: UUID, required_level: AccessLevel
    ) -> PermissionResult:
        """Verify permissions on a trip

        Args:
            owner: (UUID): The ID of the owner of the object
            permissions ([Permission]): List of permissions for the object
            subject_id (UUID): The ID requesting to verify
            required_level (AccessLevel): The access level to verify

        Returns:
            PermissionResult:
                - ALLOWED: if the user has the required permission,
                - NOT_FOUND: if the user doesn't even have read permission (as if the object doesn't exist),
                - INSUFFICIENT_PERMISSIONS: if the user can read the object but not perform the requested action.
        """
        if owner == subject_id:
            return PermissionResult.ALLOWED

        if required_level == AccessLevel.READ:
            return (
                PermissionResult.ALLOWED
                if any(perm.subject_id == subject_id and perm.access_level >= AccessLevel.READ for perm in permissions)
                else PermissionResult.NOT_FOUND
            )
        else:
            # If user has the modify or higer
            if any(perm.subject_id == subject_id and perm.access_level >= required_level for perm in permissions):
                return PermissionResult.ALLOWED
            # If subject has read but not more
            elif any(perm.subject_id == subject_id and perm.access_level >= AccessLevel.READ for perm in permissions):
                return PermissionResult.INSUFFICIENT_PERMISSIONS
            else:
                return PermissionResult.NOT_FOUND

    # Note
    @staticmethod
    def find_note_all_permissions(note_id: int) -> 'Permission':
        return [Permission.get_permission(permission) for permission in db.get_note_all_permissions(note_id)]

    # Trip
    @staticmethod
    def find_trip_all_permissions(trip_id: int) -> 'Permission':
        return [Permission.get_permission(permission) for permission in db.get_trip_all_permissions(trip_id)]

    @staticmethod
    def find_trip_user_permissions(trip_id: int, user_id: UUID) -> 'Permission':
        return Permission.get_permission(db.get_trip_permissions(trip_id, user_id))

    def create_note(self) -> 'Permission':
        """Creates a note Permission instance in the database"""
        return self.get_permission(db.create_note_permissions(self))

    def delete_note(self) -> None:
        """Removes a note Permission instance in the database"""
        return self.get_permission(db.delete_note_permissions(self.object_id, self.subject_id))

    def create_trip(self) -> 'Permission':
        """Creates a trip Permission instance in the database"""
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

        return Permission(object_id=rec.object_id, subject_id=rec.subject_id, access_level=rec.access_level)
