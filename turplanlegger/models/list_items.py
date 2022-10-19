from datetime import datetime
from typing import Dict

from turplanlegger.app import db

JSON = Dict[str, any]


class ListItem:
    """A ListItem object. Used in ItemLists.
    A ListItem object represents one item in a list.

    Args:
        owner (str): The UUID4 of the owner of the object
        item_list (int): The item_list the item belongs too
        checked (bool): Flag if the item is checked or not
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (int): Optional, the ID of the object
        owner (str): The UUID4 of the owner of the object
        item_list (int): The item_list the item belongs too
        checked (bool): Flag if the item is checked or not
        content (str): Optional, the content of the item
        create_time (datetime): Time of creation,
                                Default: datetime.now()
    """

    def __init__(self, owner: str, item_list: int, checked: bool, **kwargs) -> None:
        if not owner:
            raise ValueError("missing mandatory field 'owner'")
        if not isinstance(owner, str):
            raise TypeError("'owner' must be str")
        if not item_list:
            raise ValueError("missing mandatory field 'item_list'")
        if not isinstance(item_list, int):
            raise TypeError("'item_list' must be integer")
        if not isinstance(checked, bool):
            raise TypeError("'checked' must be boolean")

        if len(kwargs.get('content', '')) > 512:
            raise ValueError("'content' is too long")

        self.id = kwargs.get('id', None)
        self.owner = owner
        self.item_list = item_list
        self.checked = checked

        self.content = kwargs.get('content')
        self.create_time = kwargs.get('create_time', None) or datetime.now()

    @classmethod
    def parse(cls, json: JSON) -> 'ListItem':
        """Parse input JSON and return a ListItem object.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            A ListItem object

        """
        content = json.get('content', None)
        if len(content) > 512:
            raise ValueError("'content' is too long")

        return ListItem(
            id=json.get('id', None),
            owner=json.get('owner', None),
            item_list=json.get('item_list', None),
            checked=json.get('checked', False),
            content=content
        )

    @property
    def serialize(self) -> JSON:
        """Serialize a ListItem and returns it as Dict(str, any)"""
        return {
            'id': self.id,
            'owner': self.owner,
            'item_list': self.item_list,
            'content': self.content,
            'create_time': self.create_time
        }

    @property
    def mini_serialize(self) -> Dict[str, any]:
        """Serialize a minimized ListItem and returns it as Dict(str, any)
        Returns only id and contet
        """
        return {
            'id': self.id,
            'content': self.content
        }

    def create(self) -> 'ListItem':
        """Create a ListItem in the database"""
        return self.get_list_item(db.create_list_item(self))

    @staticmethod
    def delete_list_items(item_list_id: int):
        """Deletes all ListItems in a ItemList

        Args:
            item_list_id (int): Id of ItemList

        Returns:
            None
        """
        return db.delete_list_items_all(item_list_id)

    def toggle_check(self):
        """Toggle checked flag of ItemList object"""
        return db.toggle_list_item_check(self.id, False if self.checked else True)

    def delete(self) -> bool:
        """Delete a ListItem.
        Returns True if deleted"""
        return db.delete_list_item(self.id)

    # def add_list_items(self, items: item_list) -> bool:
    #     return db.add_list_items(self.id, items)

    @staticmethod
    def find_list_item(id: int) -> 'ListItem':
        """Look up a ListItem by id
        Returns ListItem or None"""
        return ListItem.get_list_item(db.get_list_item(id))

    @staticmethod
    def find_list_items(item_list_id: int, checked=None) -> '[ListItem]':
        """Looks up all ListItems in a ItemList

        Args:
            item_list_id (int): Id of ItemList
            checked (bool): Flag checked items or not
                            True: all checked items will be returned
                            False: all unchecked items will be returned
                            None: both checked and uncheck items will
                                  be returned

        Returns:
            A list of ListItem objects
        """
        return [ListItem.get_list_item(item) for item in db.get_list_items(item_list_id, checked)]

    @classmethod
    def get_list_item(cls, rec) -> 'ListItem':
        """Converts a database record to a ListItem object

        Args:
            rec (dict): Database record

        Returns:
            A  ListItem object
        """

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
