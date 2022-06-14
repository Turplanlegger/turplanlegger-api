from typing import Dict

from turplanlegger.app import db

JSON = Dict[str, any]


class Note:

    def __init__(self, owner: int, content: str, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field \'owner\'')
        if not isinstance(owner, int):
            raise TypeError('\'owner\' must be integer')
        if not content:
            raise ValueError('Missing mandatory field \'content\'')
        if not isinstance(content, str):
            raise TypeError('\'content\' must be string')

        self.owner = owner
        self.content = content
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.create_time = kwargs.get('create_time', None)

    @classmethod
    def parse(cls, json: JSON) -> 'Note':
        return Note(
            id=json.get('id', None),
            owner=json.get('owner', None),
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
            'create_time': self.create_time
        }

    def create(self) -> 'Note':
        note = self.get_note(db.create_note(self))
        return note

    def delete(self) -> bool:
        return db.delete_note(self.id)

    def rename(self) -> 'Note':
        return db.rename_note(self.id, self.name)

    def update(self) -> 'Note':
        return db.update_note(self.id, self.content)

    @staticmethod
    def find_note(id: int) -> 'Note':
        return Note.get_note(db.get_note(id))

    def change_owner(self, owner: int) -> 'Note':
        if self.owner == owner:
            raise ValueError('new owner is same as old')

        return Note.get_note(db.change_note_owner(self.id, owner))

    @classmethod
    def get_note(cls, rec) -> 'Note':
        if isinstance(rec, dict):
            return Note(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                name=rec.get('name', None),
                content=rec.get('content', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return Note(
                id=rec.id,
                owner=rec.owner,
                name=rec.name,
                content=rec.content,
                create_time=rec.create_time
            )
