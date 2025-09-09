import json
import unittest
from uuid import uuid4

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class RoutesPermissionTestCase(unittest.TestCase):
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
                id=str(uuid4()),
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )
        cls.user2 = User.create(
            User(
                id=str(uuid4()),
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


        routeGeometry = {
            'type': 'LineString',
            'coordinates': (
                [11.615295, 60.603483],
                [11.638641, 60.612921],
                [11.6819, 60.613258],
                [11.697693, 60.601797],
                [11.712112, 60.586622],
                [11.703873, 60.574476],
                [11.67984, 60.568064],
                [11.640015, 60.576838],
                [11.611862, 60.587296],
            ),
        }
        routeGeometry2 = {
            'type': 'LineString',
            'coordinates': (
                [11.615296, 60.603482],
                [11.638641, 60.612921],
                [11.6819, 60.613258],
                [11.697693, 60.601797],
                [11.712112, 60.586622],
                [11.703873, 60.574476],
                [11.67984, 60.568064],
                [11.640015, 60.576838],
                [11.611862, 60.587296],
            ),
        }
        cls.route = {'route': routeGeometry}
        cls.route_no_geometry = {}

        cls.route_read = {
            'route': routeGeometry,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.route_modify = {
            'route': routeGeometry,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.route_delete = {
            'route': routeGeometry,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'DELETE',
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
        db.truncate_table('notes')
        db.truncate_table('note_permissions')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_add_route_ok(self):
        response = self.client.post('/routes', data=json.dumps(self.route_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], str(self.user1.id))
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['permissions'][0]['object_id'], data['id'])
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))
