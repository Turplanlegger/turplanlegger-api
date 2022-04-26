from datetime import datetime
from typing import Dict

from turplanlegger.app import db

JSON = Dict[str, any]


class ListItem:

    def __init__(self, owner: int, list: int, checked: bool, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field "owner"')
        if not isinstance(owner, int):
            raise TypeError('"owner" must be integer')
        if not list:
            raise ValueError('Missing mandatory field "list"')
        if not isinstance(list, int):
            raise TypeError('"list" must be integer')
        # if not checked:
        #     raise ValueError('Missing mandatory field "checked"')
        if not isinstance(checked, bool):
            raise TypeError('"checked" must be boolean')

        self.id = kwargs.get('id', 0)
        self.owner = owner
        self.list = list
        self.checked = checked
        self.content = kwargs.get('content')
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'ListItem':
        return ListItem(
            id=json.get('id', None),
            owner=json.get('owner', None),
            list=json.get('list', None),
            checked=json.get('checked', False),
            content=json.get('content', None),
        )

    @property
    def serialize(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'owner': self.owner,
            'list': self.list,
            'content': self.content,
            'create_time': self.create_time
        }

    @property
    def mini_serialize(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'content': self.content
        }

    def create(self) -> 'ListItem':
        return self.get_list_item(db.create_list_item(self))

    @staticmethod
    def delete_list_items(list_id: int):
        return(db.delete_list_items_all(list_id))

    def delete(self) -> bool:
        return db.delete_list_item(self.id)

    # def rename(self) -> 'List':
    #     return db.rename_list(self.id, self.name)

    # def add_list_items(self, items: list) -> bool:
    #     return db.add_list_items(self.id, items)

    @staticmethod
    def find_list_item(id: int) -> 'ListItem':
        return(ListItem.get_list_item(db.get_list_item(id)))

    @staticmethod
    def find_list_items(list_id: int, checked=None) -> 'ListItem':
        return [ListItem.get_list_item(item) for item in db.get_list_items(list_id, checked)]

    @classmethod
    def get_list_item(cls, rec) -> 'ListItem':
        if isinstance(rec, dict):
            return ListItem(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                list=rec.get('list', None),
                checked=rec.get('checked', False),
                content=rec.get('content', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return ListItem(
                id=rec.id,
                owner=rec.owner,
                list=rec.list,
                checked=rec.checked,
                content=rec.content,
                create_time=rec.create_time
            )
