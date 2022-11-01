from datetime import datetime
from typing import Dict

from flask import g

from turplanlegger.app import db
from turplanlegger.models.list_items import ListItem

JSON = Dict[str, any]


class ItemList:
    """A ItemList object. An object containing multiple
    ListItems to create a list used for planning.

    E.g shopping list, packing list, name list

    Args:
        owner (str): The UUID4 of the owner of the object
        type (str): The type of list
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (int): Optional, the ID of the object
        owner (str): The UUID4 of the owner of the object
        type (str): The type of list
        name (str): Optional, name of the list
                    Default: empty list
        items (list): List of items that are unchecked
                      Default: empty list
        items_checked (list): list of items that are checked
        create_time (datetime): Time of creation,
                                Default: datetime.now()
    """

    def __init__(self, owner: str, type: str, **kwargs) -> None:
        if not owner:
            raise ValueError("missing mandatory field 'owner'")
        if not isinstance(owner, str):
            raise TypeError("'owner' must be str")
        if not type:
            raise ValueError("missing mandatory field 'type'")
        if not isinstance(type, str):
            raise TypeError("'type' must be string")

        name = kwargs.get('name', None)
        if name is not None and len(name) > 512:
            raise ValueError("'name' is too long")

        self.id = kwargs.get('id', None)
        self.owner = owner
        self.name = name
        self.type = type
        self.items = kwargs.get('items', [])
        self.items_checked = kwargs.get('items_checked', [])
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'ItemList':
        """Parse input JSON and return a ItemList object.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            A ItemList object
        """

        items = json.get('items', [])
        if not isinstance(items, list):
            raise TypeError("'items' must be JSON list")
        for i, item in enumerate(items):
            if item is not None and len(item) > 512:
                raise ValueError(f"item {i+1}:'{item}' is too long, max 512 char")

        items_checked = json.get('items_checked', [])
        if not isinstance(items_checked, list):
            raise TypeError("'items_checed' must be JSON list")
        for i, item in enumerate(items_checked):
            if item is not None and len(item) > 512:
                raise ValueError(f"checked item {i+1}:'{item}' is too long, max 512 char")

        return ItemList(
            id=json.get('id', None),
            owner=g.user.id,
            name=json.get('name', None),
            type=json.get('type', None),
            items=items,
            items_checked=items_checked
        )

    @property
    def serialize(self) -> JSON:
        """Serialize a ItemList and returns it as Dict(str, any)"""
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
        """Create a ItemList in the database
        Will also create ListItems object
        and add them to the ItemList object
        """
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
        """
        Deletes the ItemList along with any
        ListItem objects
        """
        if self.items or self.items_checked:
            ListItem.delete_list_items(self.id)

        return db.delete_item_list(self.id)

    def rename(self) -> 'ItemList':
        """Renames the ItemList"""
        return ItemList.get_item_list(db.rename_item_list(self.id, self.name))

    @staticmethod
    def find_item_list(id: int) -> 'ItemList':  # Add a method for getting list without lists_items
        """Looks a ItemList based on id

        Args:
            id (int): Id of ItemList

        Returns:
            A ItemList
        """
        return ItemList.get_item_list(db.get_item_list(id))

    @staticmethod
    def find_item_list_by_owner(owner_id: str) -> '[ItemList]':
        """Looks ItemLists by owner

        Args:
            owner_id (str): Id (uuid4) of owner

        Returns:
            A list of ItemList objects
        """
        return [ItemList.get_item_list(item_list) for item_list in db.get_item_list_by_owner(owner_id)]

    def change_owner(self) -> 'ItemList':
        """Changes owner of the ItemList"""
        return ItemList.get_item_list(db.change_item_list_owner(self.id, self.owner))

    @classmethod
    def get_item_list(cls, rec) -> 'ItemList':
        """Converts a database record to a ItemList object

        Args:
            rec (dict): Database record

        Returns:
            A  ItemList object
        """
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
