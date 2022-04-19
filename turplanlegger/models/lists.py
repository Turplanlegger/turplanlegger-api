from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

from turplanlegger.app import db

JSON = Dict[str, any]


class List:

    def __init__(self, owner: int, name: str, type: str, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field "owner"')
        if not isinstance(owner, int):
            raise TypeError('"owner" must be integer')
        if not name:
            raise ValueError('Missing mandatory field "name"')
        if not type:
            raise ValueError('Missing mandatory field "type"')
        if not isinstance(type, str):
            raise TypeError('"type" must be string')

        self.id = kwargs.get('id', 0)
        self.owner = owner
        self.name = name
        self.type = type
        self.items = kwargs.get('items', [])
        self.items_checked = kwargs.get('items_checked', [])
        self.create_time = datetime.now()

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
            'items': self.items,
            'items_checked': self.items_checked,
            'create_time': self.create_time
        }

    def create(self) -> 'List':
        list = self.get_list(db.create_list(self))
        print(list)
        if self.items:
            items = [
                {
                    'content':item,
                    'checked': False,
                    'list': list.id,
                    'owner': list.owner
                } for item in self.items
            ]
            items = [db.add_list_item(item) for item in items]
            items = [self.get_list_item(item) for item in items]
            list.items = items
            print(list.items)

        if self.items_checked:
            items_checked = [
                {
                    'content':item,
                    'checked': True,
                    'list': list.id,
                    'owner': list.owner
                } for item in self.items_checked
            ]
            items_checked = [db.add_list_item(item) for item in items_checked]
            items_checked = [self.get_list_item(item) for item in items_checked]
            list.items_checked = items_checked
            print(list.items_checked)

        return list

    def add_list_items(self, items: list) -> bool:
        return db.add_list_items(self.id, items)

    # def __repr__(self) -> str:
    #     return 'List(id={!r}, request_id={!r}, content={!r}, type_id={!r}, author={!r}, create_time={!r}'.format(
    #         self.id, self.request_id, self.content, self.type_id, self.author, self.create_time
    #     )

    @staticmethod
    def find_list(id: int) -> 'List':
        return(List.get_list(db.get_list(id)))

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
                items=None,
                items_checked=None,
                create_time=rec.create_time
            )

    def get_list_item(self, rec):
        if isinstance(rec, dict):
            return {
                'id': rec.get('id', None),
                'content': rec.get('owner', None)
            }
        elif isinstance(rec, tuple):
            return {
                'id': rec.id,
                'content': rec.content
            }

