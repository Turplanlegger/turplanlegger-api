from datetime import datetime
from typing import Dict, List

from turplanlegger.app import db
from turplanlegger.models.list_items import ListItem

JSON = Dict[str, any]


class ItemList:  # This class has to be renamed

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
    def parse(cls, json: JSON) -> 'ItemList':
        if not isinstance(json.get('items', []), list):
            raise TypeError('"items" must be list')
        if not isinstance(json.get('items_checked', []), list):
            raise TypeError('"items_checked" must be list')
        return ItemList(
            id=json.get('id', 0),
            owner=json.get('owner', None),
            name=json.get('name', None),
            type=json.get('type', None),
            items=json.get('items', []),
            items_checked=json.get('items_checked', [])
        )

    @property
    def serialize(self) -> JSON:
        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'type': self.type,
            'items': [item.serialize for item in self.items],
            'items_checked': [item.serialize for item in self.items_checked],
            'create_time': self.create_time
        }

    def create(self) -> 'ItemList':
        item_list = self.get_item_list(db.create_item_list(self))
        if self.items:
            items = [ListItem(
                owner=item_list.owner,
                item_list=item_list.id,
                checked=False,
                content=item) for item in self.items]
            items = [item.create() for item in items]
            item_list.items, self.items = [items, items]

        if self.items_checked:
            items_checked = [ListItem(
                owner=item_list.owner,
                item_list=item_list.id,
                checked=True,
                content=item) for item in self.items_checked]
            items_checked = [item.create() for item in items_checked]
            item_list.items_checked, self.items_checked = [items_checked, items_checked]

        return item_list

    def delete(self) -> bool:
        if self.items or self.items_checked:
            ListItem.delete_list_items(self.id)

        return db.delete_item_list(self.id)

    def rename(self) -> 'ItemList':
        return db.rename_item_list(self.id, self.name)

    @staticmethod
    def find_item_list(id: int) -> 'ItemList':  # Add a method for getting list without lists_items
        return ItemList.get_item_list(db.get_item_list(id))

    def change_owner(self, owner: int) -> 'ItemList':
        if self.owner == owner:
            raise ValueError('new owner is same as old')

        # A user object should be parsed/passed
        # Return a boolean, don't get the list unless it's used
        return ItemList.get_item_list(db.change_item_list_owner(self.id, owner))

    @classmethod
    def get_item_list(cls, rec) -> 'ItemList':
        if isinstance(rec, dict):
            return ItemList(
                id=rec.get('id', None),
                owner=rec.get('owner', None),
                name=rec.get('name', None),
                type=rec.get('type', None),
                items=rec.get('items', None),
                items_checked=rec.get('items_checked', None),
                create_time=rec.get('created', None)
            )
        elif isinstance(rec, tuple):
            return ItemList(
                id=rec.id,
                owner=rec.owner,
                name=rec.name,
                type=rec.type,
                items=ListItem.find_list_items(rec.id, checked=False),
                items_checked=ListItem.find_list_items(rec.id, checked=True),
                create_time=rec.create_time
            )
