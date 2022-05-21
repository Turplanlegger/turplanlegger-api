import json
import unittest

from turplanlegger.app import create_app  # ,  db


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        # Users isn't implemented yet, so they have to be created manually for the time being
        self.user1 = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no'
        }
        self.user1 = {
            'name': 'Kari',
            'last_name': 'Nordamnn',
            'email': 'kari.nordmann@norge.no'
        }

        self.route = {
            'route': '{\"type\":\"LineString\",\"coordinates\":[[11.615295,60.603483],[11.638641,60.612921],[11.6819,60.613258],[11.697693,60.601797],[11.712112,60.586622],[11.703873,60.574476],[11.67984,60.568064],[11.640015,60.576838],[11.611862,60.587296]]}',
            'owner': 1,
        }

        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):
        db.destroy()

    def test_create_route(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['route']['owner'], 1)  # Update to user created