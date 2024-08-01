from typing import Dict

from flask import g

from turplanlegger.app import db

JSON = Dict[str, any]


class Note:
    def __init__(self, owner: str, content: str, **kwargs) -> None:
        if not owner:
            raise ValueError("Missing mandatory field 'owner'")
        if not isinstance(owner, str):
            raise TypeError("'owner' must be str")
        if not content:
            raise ValueError("Missing mandatory field 'content'")
        if not isinstance(content, str):
            raise TypeError("'content' must be string")

        self.owner = owner
        self.content = content
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.create_time = kwargs.get('create_time', None)
        self.update_time = kwargs.get('update_time', None)
        self.deleted = kwargs.get('deleted', None)
        self.delete_time = kwargs.get('delete_time', None)

    def __repr__(self):
        return (
            f"Note(id='{self.id}', owner='{self.owner}', "
            f"name='{self.name}', content='{self.content}', "
            f'create_time={self.create_time}, update_time={self.update_time}, '
            f'deleted={self.deleted}, delete_time={self.delete_time})'
        )

    @classmethod
    def parse(cls, json: JSON) -> 'Note':
        return Note(
            id=json.get('id', None),
            owner=g.user.id,
            content=json.get('content', None),
            name=json.get('name', None),
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'content': self.content,
            'create_time': self.create_time,
        }

    def create(self) -> 'Note':
        note = self.get_note(db.create_note(self))
        return note

    def update(self, updated_fields) -> 'Note':
        return db.update_note(self, updated_fields)

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

    @classmethod
    def get_note(cls, rec) -> 'Note':
        if rec is None:
            return None

        return Note(
            id=rec.id,
            owner=rec.owner,
            name=rec.name,
            content=rec.content,
            create_time=rec.create_time,
            update_time=rec.update_time,
            deleted=rec.deleted,
            delete_time=rec.delete_time,
        )
