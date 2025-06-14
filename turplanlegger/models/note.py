from typing import Dict
from uuid import UUID

from flask import g

from turplanlegger.app import db
from turplanlegger.models.permission import Permission

JSON = Dict[str, any]


class Note:
    """A note object. For saving and sharing content.

    Args:
        owner (UUID): The UUID4 of the owner of the note
        content (str): The main text content of the note
        **kwargs: Arbitrary keyword arguments

    Attributes:
        owner (UUID): The UUID4 of the owner of the note
        content (str): The main text content of the note
        id (int): Optional, the ID of the note
        name (str): Optional, the name/title of the note
        permissions (list): List of permissions related to the note
        create_time (datetime): Time of creation
        update_time (datetime): Time of last update
        deleted (bool): Flag indicating if the note has been deleted
        delete_time (datetime): Time the note was deleted
    """

    def __init__(self, owner: UUID, content: str, **kwargs) -> None:
        if not owner:
            raise ValueError("Missing mandatory field 'owner'")
        if not isinstance(owner, UUID):
            raise TypeError("'owner' must be UUID")
        if not content:
            raise ValueError("Missing mandatory field 'content'")
        if not isinstance(content, str):
            raise TypeError("'content' must be string")

        self.owner = owner
        self.content = content
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.permissions = kwargs.get('permissions', None)
        self.create_time = kwargs.get('create_time', None)
        self.update_time = kwargs.get('update_time', None)
        self.deleted = kwargs.get('deleted', None)
        self.delete_time = kwargs.get('delete_time', None)

    def __repr__(self):
        return (
            f"Note(id='{self.id}', owner='{self.owner}', "
            f"name='{self.name}', content='{self.content}', "
            f'permissions={self.permissions}), '
            f'create_time={self.create_time}, update_time={self.update_time}, '
            f'deleted={self.deleted}, delete_time={self.delete_time})'
        )

    @classmethod
    def parse(cls, json: JSON) -> 'Note':
        permissions = json.get('permissions', [])
        if not isinstance(permissions, list):
            raise TypeError('permissions has to be a list of permission objects')
        permissions[:] = [Permission.parse(permission) for permission in permissions]

        return Note(
            id=json.get('id', None),
            owner=g.user.id,
            content=json.get('content', None),
            name=json.get('name', None),
            permissions=permissions,
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'content': self.content,
            'create_time': self.create_time,
            'permissions': [permission.serialize for permission in self.permissions],
        }

    def create(self) -> 'Note':
        note = self.get_note(db.create_note(self))
        if self.permissions:
            permissions = []
            for permission in self.permissions:
                permission.object_id = note.id
                permissions.append(permission.create_note())
            note.permissions = permissions
        return note

    def update(self) -> 'Note':
        return Note.get_note(db.update_note(self))

    def delete(self) -> bool:
        return db.delete_note(self.id)

    def rename(self) -> 'Note':
        return db.rename_note(self.id, self.name)

    def update_content(self) -> 'Note':
        return db.update_note_content(self.id, self.content)

    @staticmethod
    def find_note(id: int) -> 'Note':
        return Note.get_note(db.get_note(id))

    @staticmethod
    def find_note_by_owner(owner_id: str) -> 'Note':
        return [Note.get_note(note) for note in db.get_note_by_owner(owner_id)]

    def change_owner(self, owner: str) -> 'Note':
        if self.owner == owner:
            raise ValueError('new owner is same as old')

        return Note.get_note(db.change_note_owner(self.id, owner))

    @staticmethod
    def add_permissions(permissions: tuple[Permission]) -> tuple[Permission]:
        return tuple(perm.create_note() for perm in permissions)

    @staticmethod
    def delete_permission(permission: Permission) -> None:
        return permission.delete_note()

    @classmethod
    def get_note(cls, rec) -> 'Note':
        if rec is None:
            return None

        return Note(
            id=rec.id,
            owner=rec.owner,
            name=rec.name,
            content=rec.content,
            permissions=Permission.find_note_all_permissions(rec.id),
            create_time=rec.create_time,
            update_time=rec.update_time,
            deleted=rec.deleted,
            delete_time=rec.delete_time,
        )
