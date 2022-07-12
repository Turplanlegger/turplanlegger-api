import json
import unittest

from turplanlegger.app import create_app, db


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'CREATE_ADMIN_USER': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        response = self.client.post(
            '/login',
            data=json.dumps(
                {
                    'email': self.app.config.get('ADMIN_EMAIL'),
                    'password': self.app.config.get('ADMIN_PASSWORD')
                }
            ),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.headers = {
            'Authorization': f'Bearer {data["token"]}'
        }

    def tearDown(self):
        db.destroy()

    def test_get_admin_user(self):

        response = self.client.get('/user/1', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['user']['id'], 1)
        self.assertEqual(data['user']['name'], 'Admin')
        self.assertEqual(data['user']['last_name'], 'Nimda')
        self.assertEqual(data['user']['email'], self.app.config.get('ADMIN_EMAIL'))
        self.assertEqual(data['user']['auth_method'], 'basic')
        self.assertEqual(data['user']['private'], True)
