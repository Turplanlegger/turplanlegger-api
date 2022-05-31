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
            'email': 'ola.nordmann@norge.no'
        }
        self.user2 = {
            'name': 'Kari',
            'last_name': 'Nordamnn',
            'email': 'kari.nordmann@norge.no'
        }

    def tearDown(self):
        db.destroy()

    def test_get_user_not_found(self):
        response = self.client.get('/user/2')
        self.assertEqual(response.status_code, 404)
