from uuid import UUID


def to_uuid(value: any) -> UUID:
    if isinstance(value, UUID):
        return value
    elif isinstance(value, str):
        try:
            return UUID(value)
        except ValueError as e:
            raise ValueError(f'Invalid UUID string: {value}') from e
    else:
        raise TypeError('id must be a uuid.UUID or a valid UUID string')
