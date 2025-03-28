import json
import unittest

from turplanlegger.app import create_app, db


class UsersTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'CREATE_ADMIN_USER': True,
            'ADMIN_EMAIL': 'admin@admintestturplanlegger.com',
            'ADMIN_PASSWORD': 'tesme',
        }

        cls.app = create_app(cls.config)
        cls.client = cls.app.test_client()

        response = cls.client.post(
            '/login',
            data=json.dumps(
                {'email': cls.app.config.get('ADMIN_EMAIL'), 'password': cls.app.config.get('ADMIN_PASSWORD')}
            ),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login')
        data = json.loads(response.data.decode('utf-8'))

        cls.headers = {'Authorization': f'Bearer {data["token"]}'}

    def tearDown(self):
        db.destroy()

    def test_get_admin_user(self):
        response = self.client.get(f'/users?email={self.config.get("ADMIN_EMAIL")}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['user']['name'], 'Admin')
        self.assertEqual(data['user']['last_name'], 'Nimda')
        self.assertEqual(data['user']['email'], self.config.get('ADMIN_EMAIL'))
        self.assertEqual(data['user']['auth_method'], 'basic')
        self.assertEqual(data['user']['private'], True)
