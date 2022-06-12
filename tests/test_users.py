import json
import unittest

from turplanlegger.app import create_app, db


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        self.user1 = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no',
            'auth_method': 'basic',
            'private': False
        }
        self.user2 = {
            'name': 'Kari',
            'email': 'kari.nordmann@norge.no'
        }
        self.user3 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'invalid.com',
            'auth_method': 'basic'
        }
        self.user4 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'private': True
        }

        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):
        db.destroy()

    def test_get_user_not_found(self):
        response = self.client.get('/user/1')
        self.assertEqual(response.status_code, 404)

    def test_create_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['user']['name'], self.user1['name'])
        self.assertEqual(data['user']['last_name'], self.user1['last_name'])
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], self.user1['private'])

    def test_create_public_user(self):
        response = self.client.post('/user', data=json.dumps(self.user4), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['user']['name'], self.user4['name'])
        self.assertEqual(data['user']['last_name'], self.user4['last_name'])
        self.assertEqual(data['user']['email'], self.user4['email'])
        self.assertEqual(data['user']['auth_method'], self.user4['auth_method'])
        self.assertEqual(data['user']['private'], self.user4['private'])

    def test_delete_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.delete(f'/user/{data["id"]}')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/user/{data["id"]}')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def test_create_user_no_last_name(self):
        response = self.client.post('/user', data=json.dumps(self.user2), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email(self):
        response = self.client.post('/user', data=json.dumps(self.user3), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_rename_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            f'/user/{data["id"]}/rename',
            data=json.dumps({'name': 'Petter', 'last_name': 'Smart'}),
            headers=self.headers
        )
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user']['name'], 'Petter')
        self.assertEqual(data['user']['last_name'], 'Smart')
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], self.user1['private'])

    def test_change_private(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f'/user/{data["id"]}/private')

        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/user/{data["id"]}')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['user']['name'], self.user1['name'])
        self.assertEqual(data['user']['last_name'], self.user1['last_name'])
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], True)
