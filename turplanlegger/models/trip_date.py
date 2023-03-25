from datetime import datetime
from typing import Dict, NamedTuple

from flask import g

from turplanlegger.app import db

JSON = Dict[str, any]


class TripDate:
    """TripDate object defines start- and end-date for a trip.
    A TripDate does not have a public/private flag, it's inherited
    from the trip (parent)

    Args:
        owner (str): Id of the owner
        start_time (datetime): Datetime object as start date
        end_time (datetime): Datetime object as end date
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        owner (str): The UUID4 of the owner of the object
        id (int): Optional, the ID of the object
        trip_id (int): The ID of the trip (parent)
        start_time (datetime): Datetime object as start date
        end_time (datetime): Datetime object as end date
        create_time (datetime): Time of creation,
                                Default: datetime.now()
        deleted (bool): Flag if the object has been logically deleted
                        Default : False
        delete_time (datetime): Datetime instance of time of deletion


    """
    def __init__(self, owner: str, start_time: datetime, end_time: datetime, **kwargs) -> None:
        if not owner:
            raise ValueError('Missing mandatory field \'owner\'')
        if not isinstance(owner, str):
            raise TypeError('\'owner\' must be string')
        if not start_time:
            raise ValueError('Missing mandatory field \'start_time\'')
        if not isinstance(start_time, datetime):
            raise TypeError('\'start_time\' must be an datetime instance')
        if not end_time:
            raise ValueError('Missing mandatory field \'end_time\'')
        if not isinstance(end_time, datetime):
            raise TypeError('\'end_time\' must be an datetime instance')

        self.owner = owner
        self.start_time = start_time
        self.end_time = end_time
        self.id = kwargs.get('id', None)
        self.trip_id = kwargs.get('trip_id', None)
        self.create_time = kwargs.get('create_time', None) or datetime.now()
        self.deleted = kwargs.get('deleted', False)
        self.delete_time = kwargs.get('delete_time', None)

    def __repr__(self):
        return (
            'TripDate('
            f'id: {self.id}, trip_id: {self.trip_id}, owner: {self.owner}, '
            f'start_time: {self.start_time}, end_time: {self.end_time}, '
            f'deleted: {self.deleted}, delete_time: {self.delete_time}, '
            f'create_time: {self.create_time})'
        )
    @classmethod
    def parse(cls, json: JSON) -> 'TripDate':
        """Parse input JSON and return an TripDate instance.

        Args:
            json (Dict[str, any]): JSON input object

        Returns:
            An TripDate instance
        """
        start_time = datetime.fromisoformat(json.get('start_time', None))
        end_time = datetime.fromisoformat(json.get('end_time', None))

        if start_time > end_time:
            raise ValueError('start_time can not be before end_time')

        return TripDate(
            id=json.get('id', None),
            owner=g.user.id,
            start_time=start_time,
            end_time=end_time
        )

    @property
    def serialize(self) -> JSON:
        """Serialize the TripDate instance and returns it as Dict(str, any)"""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'owner': self.owner,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'create_time': self.create_time
        }

    def create(self) -> 'TripDate':
        """Creates the TripDate instance in the database"""
        return self.get_trip_date(db.create_trip_date(self))

    def delete(self) -> bool:
        """Deletes the TripDate object from the database
        Returns True if deleted"""
        return db.delete_trip_date(self.id)

    @staticmethod
    def find_by_trip_id(trip_id: int) -> ['TripDate']:
        """Looks up trip dates by trip id

        Args:
            trip_id (int): id of trip

        Returns:
            A list of TripDate instances
        """
        return [td for td in db.get_trip_dates_by_trip(trip_id)]

    @classmethod
    def get_trip_date(cls, rec: NamedTuple) -> 'TripDate':
        """Converts a database record to an TripDate instance

        Args:
            rec (NamedTuple): Database record

        Returns:
            An TripDate instance
        """
        if rec is None:
            return None

        return TripDate(
            id=rec.id,
            trip_id=rec.trip_id,
            owner=rec.owner,
            start_time=rec.start_time,
            end_time=rec.end_time,
            create_time=rec.create_time,
            deleted=rec.deleted,
            delete_time=rec.delete_time
        )
