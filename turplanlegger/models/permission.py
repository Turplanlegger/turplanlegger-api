from enum import Enum


class AccessLevel(Enum):
    READ = 'read'
    MODIFY = 'modify'
    DELETE = 'delete'
