from datetime import datetime
from typing import Dict

from turplanlegger.app import db

JSON = Dict[str, any]


class ListItem:

    def __init__(self, owner: int, item_list: int, checked: bool, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field "owner"')
        if not isinstance(owner, int):
            raise TypeError('"owner" must be integer')
        if not item_list:
            raise ValueError('Missing mandatory field "item_list"')
        if not isinstance(item_list, int):
            raise TypeError('"item_list" must be integer')
        # if not checked:
        #     raise ValueError('Missing mandatory field "checked"')
        if not isinstance(checked, bool):
            raise TypeError('"checked" must be boolean')

        self.id = kwargs.get('id', 0)
        self.owner = owner
        self.item_list = item_list
        self.checked = checked
        self.content = kwargs.get('content')
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'ListItem':
        return ListItem(
            id=json.get('id', None),
            owner=json.get('owner', None),
            item_list=json.get('item_list', None),
            checked=json.get('checked', False),
            content=json.get('content', None),
        )

    @property
    def serialize(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'owner': self.owner,
            'item_list': self.item_list,
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
    def delete_list_items(item_list_id: int):
        return(db.delete_list_items_all(item_list_id))

    def delete(self) -> bool:
        return db.delete_list_item(self.id)

    # def add_list_items(self, items: item_list) -> bool:
    #     return db.add_list_items(self.id, items)

    @staticmethod
    def find_list_item(id: int) -> 'ListItem':
        return(ListItem.get_list_item(db.get_list_item(id)))

    @staticmethod
    def find_list_items(item_list_id: int, checked=None) -> 'ListItem':
        return [ListItem.get_list_item(item) for item in db.get_list_items(item_list_id, checked)]

    @classmethod
    def get_list_item(cls, rec) -> 'ListItem':
        if isinstance(rec, dict):
            return ListItem(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                item_list=rec.get('item_list', None),
                checked=rec.get('checked', False),
                content=rec.get('content', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return ListItem(
                id=rec.id,
                owner=rec.owner,
                item_list=rec.item_list,
                checked=rec.checked,
                content=rec.content,
                create_time=rec.create_time
            )
