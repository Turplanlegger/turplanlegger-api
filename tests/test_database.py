import datetime
import json
import unittest
from uuid import uuid4

from collections import namedtuple

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class UsersTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'INFO',
            'CREATE_ADMIN_USER': False
        }

        cls.app = create_app(config)
        cls.client = cls.app.test_client()
        cls.hashed_password = hash_password('test')

    def setUp(self):
        self.test_user = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=self.hashed_password
            )
        )

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.test_user.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.headers_json = {
            'Content-type': 'application/json',
            'Authorization': f'Bearer {data["token"]}'
        }
        self.headers = {
            'Authorization': f'Bearer {data["token"]}'
        }

    def tearDown(self):
        db.truncate_table('users')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_bogus_query_should_rollback(self):
        insert = """
            INSERT INTO users (id, name, last_name, email, auth_method, password,  private, create_time)
            VALUES (%(id)s, %(name)s, %(last_name)s, %(email)s, %(auth_method)s, %(password)s, %(private)s, %(create_time)s)
            ON CONFLICT DO NOTHING
            RETURNING *
        """

        now = datetime.datetime.utcnow()

        faulty_vars = {
            'id': 1,
            'name': 'n',
            'last_name': 'l',
            'email': 'e',
            'auth_method': 'a',
            'password': 'adsadsa',
            'private': 'NEI',
            'create_time': now
        }

        with self.assertRaises(Exception) as cm:
            db._insert(insert, faulty_vars)
            self.assertIn(cm.exception, 'invalid input syntax for type boolean: "NEI"')

        correct_vars = {
            'id': 1,
            'name': 'n',
            'last_name': 'l',
            'email': 'e',
            'auth_method': 'a',
            'password': 'adsadsa',
            'private': False,
            'create_time': now
        }

        Row = namedtuple('Row', ['id','name', 'last_name', 'email', 'auth_method', 'password', 'private', 'create_time', 'deleted', 'delete_time'])
        correct = Row('1', 'n', 'l', 'e', 'a', 'adsadsa', False, now, False, None)
        
        res = db._insert(insert, correct_vars)
        self.assertEqual(correct, res)