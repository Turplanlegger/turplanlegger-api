from datetime import datetime
from typing import Dict, List

from turplanlegger.app import db
from turplanlegger.models.list_item import ListItem

JSON = Dict[str, any]


class List:  # This class has to be renamed

    def __init__(self, owner: int, type: str, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field "owner"')
        if not isinstance(owner, int):
            raise TypeError('"owner" must be integer')
        if not type:
            raise ValueError('Missing mandatory field "type"')
        if not isinstance(type, str):
            raise TypeError('"type" must be string')

        self.id = kwargs.get('id', 0)
        self.owner = owner
        self.name = kwargs.get('name')
        self.type = type
        self.items = kwargs.get('items', [])
        self.items_checked = kwargs.get('items_checked', [])
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'List':
        if not isinstance(json.get('items', []), list):
            raise TypeError('"items" must be list')
        if not isinstance(json.get('items_checked', []), list):
            raise TypeError('"items_checked" must be list')
        return List(
            id=json.get('id', 0),
            owner=json.get('owner', None),
            name=json.get('name', None),
            type=json.get('type', None),
            items=json.get('items', []),
            items_checked=json.get('items_checked', [])
        )

    @property
    def serialize(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'type': self.type,
            'items': [item.serialize for item in self.items],
            'items_checked': [item.serialize for item in self.items_checked],
            'create_time': self.create_time
        }

    def create(self) -> 'List':
        list = self.get_list(db.create_list(self))
        if self.items:
            items = [ListItem(
                owner=list.owner,
                list=list.id,
                checked=False,
                content=item) for item in self.items]
            items = [item.create() for item in items]
            list.items, self.items = [items, items]

        if self.items_checked:
            items_checked = [ListItem(
                owner=list.owner,
                list=list.id,
                checked=True,
                content=item) for item in self.items_checked]
            items_checked = [item.create() for item in items_checked]
            list.items_checked, self.items_checked = [items_checked, items_checked]

        return list

    def rename(self) -> 'List':
        return db.rename_list(self.id, self.name)

    @staticmethod
    def find_list(id: int) -> 'List':
        return List.get_list(db.get_list(id))

    @classmethod
    def get_list(cls, rec) -> 'List':
        if isinstance(rec, dict):
            return List(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                name=rec.get('name', None),
                type=rec.get('type', None),
                items=rec.get('items', None),
                items_checked=rec.get('items_checked', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return List(
                id=rec.id,
                owner=rec.owner,
                name=rec.name,
                type=rec.type,
                items=ListItem.find_list_items(rec.id, checked=False),
                items_checked=ListItem.find_list_items(rec.id, checked=True),
                create_time=rec.create_time
            )
