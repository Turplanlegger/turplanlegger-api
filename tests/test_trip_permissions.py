import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class TripsPermissionsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'INFO',
            'CREATE_ADMIN_USER': True,
        }

        cls.app = create_app(config)
        cls.client = cls.app.test_client()

        cls.user1 = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )
        cls.user2 = User.create(
            User(
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )
        cls.user3 = User.create(
            User(
                name='Bård',
                last_name='Nordamnn',
                email='baard.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )

        cls.trip1 = {
            'name': 'trippin pete perms',
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }

        # User 1
        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user1.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login user 1')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json_user1 = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.headers_user1 = {'Authorization': f'Bearer {data["token"]}'}

        # User 2
        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user2.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login user 2')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json_user2 = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.headers_user2 = {'Authorization': f'Bearer {data["token"]}'}


        # User 3
        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user3.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login user 3')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json_user3 = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.headers_user3 = {'Authorization': f'Bearer {data["token"]}'}


    def tearDown(self):
        db.truncate_table('trips')
        db.truncate_table('trip_permissions')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_create_trip_with_permissions_ok(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip1),
            headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['owner'], str(self.user1.id))
        self.assertEqual(data['name'], self.trip1['name'])
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['permissions'][0]['object_id'], data['id'])
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

    def test_get_trip_with_permissions_ok(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip1),
            headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

        # User 2 - ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['trip']['permissions']), 1)
        self.assertEqual(data['trip']['permissions'][0]['subject_id'], str(self.user2.id))

        # User 3 - not ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Trip not found')
        self.assertEqual(data['detail'], 'The requested trip was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{trip_id}')
