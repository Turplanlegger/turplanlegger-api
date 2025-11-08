import json
import unittest
from uuid import uuid4, UUID

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
            'CREATE_ADMIN_USER': False,
        }

        cls.app = create_app(config)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.user_private = User.create(
            User(
                id=str(uuid4()),
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
                private=True
            )
        )
        self.user_public = User.create(
            User(
                id=str(uuid4()),
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
                private=False
            )
        )

        # User Private
        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user_private.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login user private')

        data = json.loads(response.data.decode('utf-8'))

        self.headers_json_user_private = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        self.headers_user_private = {'Authorization': f'Bearer {data["token"]}'}
        
        # User Public
        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user_public.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login user private')

        data = json.loads(response.data.decode('utf-8'))

        self.headers_json_user_public = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        self.headers_user_public = {'Authorization': f'Bearer {data["token"]}'}

    def tearDown(self):
        db.truncate_table('users')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_get_users(self):
        # Ok
        response = self.client.get(f'/users/{str(self.user_private.id)}', headers=self.headers_user_private)
        self.assertEqual(response.status_code, 200)

        # Ok
        response = self.client.get(f'/users/{str(self.user_public.id)}', headers=self.headers_user_private)
        self.assertEqual(response.status_code, 200)

        # Ok
        response = self.client.get(f'/users/{str(self.user_public.id)}', headers=self.headers_user_public)
        self.assertEqual(response.status_code, 200)

        # Not ok
        response = self.client.get(f'/users/{str(self.user_private.id)}', headers=self.headers_user_public)
        self.assertEqual(response.status_code, 404)

    def test_get_users_by_email(self):
        # Ok
        response = self.client.get('/users', query_string={'email': self.user_private.email}, headers=self.headers_user_private)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(UUID(data['user']['id']), self.user_private.id)
        self.assertEqual(data['user']['name'], self.user_private.name)
        self.assertEqual(data['user']['last_name'], self.user_private.last_name)
        self.assertEqual(data['user']['email'], self.user_private.email)
        self.assertEqual(data['user']['auth_method'], self.user_private.auth_method)
        self.assertEqual(data['user']['private'], self.user_private.private)

        # Ok
        response = self.client.get('/users', query_string={'email': self.user_public.email}, headers=self.headers_user_private)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(UUID(data['user']['id']), self.user_public.id)
        self.assertEqual(data['user']['name'], self.user_public.name)
        self.assertEqual(data['user']['last_name'], self.user_public.last_name)
        self.assertEqual(data['user']['email'], self.user_public.email)
        self.assertEqual(data['user']['auth_method'], self.user_public.auth_method)
        self.assertEqual(data['user']['private'], self.user_public.private)

        # Ok
        response = self.client.get('/users', query_string={'email': self.user_public.email}, headers=self.headers_user_public)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(UUID(data['user']['id']), self.user_public.id)
        self.assertEqual(data['user']['name'], self.user_public.name)
        self.assertEqual(data['user']['last_name'], self.user_public.last_name)
        self.assertEqual(data['user']['email'], self.user_public.email)
        self.assertEqual(data['user']['auth_method'], self.user_public.auth_method)
        self.assertEqual(data['user']['private'], self.user_public.private)

        # Not ok
        response = self.client.get('/users', query_string={'email': self.user_private.email}, headers=self.headers_user_public)
        self.assertEqual(response.status_code, 404)


    def test_delete_user(self):
        # Not ok
        response = self.client.delete(f'/users/{str(self.user_public.id)}', headers=self.headers_user_private)
        self.assertEqual(response.status_code, 403)

        # Not ok
        response = self.client.delete(f'/users/{str(self.user_private.id)}', headers=self.headers_user_public)
        self.assertEqual(response.status_code, 404)
    
        # Ok
        response = self.client.delete(f'/users/{str(self.user_private.id)}', headers=self.headers_user_private)
        self.assertEqual(response.status_code, 200)

        # Ok
        response = self.client.delete(f'/users/{str(self.user_public.id)}', headers=self.headers_user_public)
        self.assertEqual(response.status_code, 200)

    def test_rename_user(self):
        # Not ok
        response = self.client.patch(
            f'/users/{str(self.user_private.id)}/rename',
            data=json.dumps({'name': "DJ2",}),
            headers=self.headers_json_user_public,
        )
        self.assertEqual(response.status_code, 404)

        # Ok
        response = self.client.patch(
            f'/users/{str(self.user_private.id)}/rename',
            data=json.dumps({'name': "DJ",}),
            headers=self.headers_json_user_private,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(UUID(data['user']['id']), self.user_private.id)
        self.assertEqual(data['user']['name'], "DJ")
        self.assertEqual(data['user']['last_name'], self.user_private.last_name)
        self.assertEqual(data['user']['email'], self.user_private.email)
        self.assertEqual(data['user']['auth_method'], self.user_private.auth_method)
        self.assertEqual(data['user']['private'], self.user_private.private)

        # Not ok
        response = self.client.patch(
            f'/users/{str(self.user_public.id)}/rename',
            data=json.dumps({'name': "DJ3",}),
            headers=self.headers_json_user_private,
        )
        self.assertEqual(response.status_code, 403)
    
        # Ok
        response = self.client.patch(
            f'/users/{str(self.user_public.id)}/rename',
            data=json.dumps({'last_name': "DJ4",}),
            headers=self.headers_json_user_public,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(UUID(data['user']['id']), self.user_public.id)
        self.assertEqual(data['user']['name'], self.user_public.name)
        self.assertEqual(data['user']['last_name'], "DJ4")
        self.assertEqual(data['user']['email'], self.user_public.email)
        self.assertEqual(data['user']['auth_method'], self.user_public.auth_method)
        self.assertEqual(data['user']['private'], self.user_public.private)
