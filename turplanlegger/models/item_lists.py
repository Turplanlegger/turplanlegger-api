from datetime import datetime
from typing import Dict, NamedTuple

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
        private (bool): Flag if the trip is private
                        Default so False (public)
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (int): Optional, the ID of the object
        owner (str): The UUID4 of the owner of the object
        private (bool): Flag if the trip is private
                        Default so False (public)
        name (str): Optional, name of the list
                    Default: empty list
        items (list): List of items that are unchecked
                      Default: empty list
        items_checked (list): list of items that are checked
        create_time (datetime): Time of creation,
                                Default: datetime.now()
    """

    def __init__(
        self,
        owner: str,
        private: bool = True,
        **kwargs
    ) -> None:
        if not owner:
            raise ValueError("missing mandatory field 'owner'")
        if not isinstance(owner, str):
            raise TypeError("'owner' must be str")
        if not isinstance(private, bool):
            raise TypeError("'private' must be boolean")

        name = kwargs.get('name', None)
        if name is not None and len(name) > 512:
            raise ValueError("'name' is too long")

        self.id = kwargs.get('id', None)
        self.owner = owner
        self.name = name
        self.private = private
        self.items = kwargs.get('items', [])
        self.items_checked = kwargs.get('items_checked', [])
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    def __repr__(self):
        return (
            'ItemList('
            f'id: {self.id}, owner: {self.owner}, '
            f'name: {self.name}, items: {self.items},'
            f'items_checked: {self.items_checked}, '
            f'create_time: {self.create_time})'
            )

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
        items[:] = [ItemList.parse(item) for item in items]

        items_checked = json.get('items_checked', [])
        if not isinstance(items_checked, list):
            raise TypeError("'items_checed' must be JSON list")
        items_checked[:] = [ItemList.parse(item) for item in items_checked]

        return ItemList(
            id=json.get('id', None),
            owner=g.user.id,
            name=json.get('name', None),
            private=json.get('private', True),
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
            'private': self.private,
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
            items = [item.create() for item in self.items]
            item_list.items, self.items = [items, items]

        if self.items_checked:
            items_checked = [item.create() for item in self.items_checked]
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
            A ItemList along with its ListItems
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

    @staticmethod
    def find_public_item_lists() -> '[ItemList]':
        """Fetches all public ItemLists

        Returns:
            A list of ItemList objects
        """
        return [ItemList.get_item_list(item_list) for item_list in db.get_public_item_lists()]

    def change_owner(self) -> 'ItemList':
        """Changes owner of the ItemList"""
        return ItemList.get_item_list(db.change_item_list_owner(self.id, self.owner))

    @classmethod
    def get_item_list(cls, rec: NamedTuple) -> 'ItemList':
        """Converts a database record to a ItemList object

        Args:
            rec (NamedTuple): Database record

        Returns:
            An ItemList instance
        """

        if rec is None:
            return None

        return ItemList(
            id=rec.id,
            owner=rec.owner,
            name=rec.name,
            private=rec.private,
            items=ListItem.find_list_items(rec.id, checked=False),
            items_checked=ListItem.find_list_items(rec.id, checked=True),
            create_time=rec.create_time
        )
