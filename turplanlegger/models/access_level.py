
from enum import EnumMeta, StrEnum


class CachedEnumMeta(EnumMeta):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get index based on definition order
        for index, member in enumerate(cls):
            member._index = index

class AccessLevel(StrEnum, metaclass=CachedEnumMeta):
    READ = 'READ'
    MODIFY = 'MODIFY'
    DELETE = 'DELETE'

    def __lt__(self, other):
        return self._index < other._index

    def __le__(self, other):
        return self._index < other._index

    def __gt__(self, other):
        return self._index < other._index

    def __ge__(self, other):
        return self._index < other._index
