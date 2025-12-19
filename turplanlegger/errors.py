from enum import Enum


class ErrorMessage(Enum):
    """User-facing error messages used across the app."""

    # Generic
    GENERIC_UNKNOWN = 'Unknown error'

    # Permission
    PERMS_INSUFFICIENT = 'Insufficient permissions'

    # Trip
    TRIP_FAILED_LOOKUP = 'Failed to look up trip'
    TRIP_NOT_FOUND = 'Trip not found'
    TRIP_NOT_FOUND_LONG = 'The requested trip was not found'
    TRIP_PERMS_INSUFFICIENT_MODIFY = 'Not sufficient permissions to modify the trip'
    TRIP_FAILED_ADD_NOTE = 'Failed to add note to trip'

    def __str__(self) -> str:
        return self.value
