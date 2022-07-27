import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class TripsTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        self.user1 = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )
        self.user2 = User.create(
            User(
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )
        self.route = {
            'route': ('{\"type\":\"LineString\",\"coordinates\":[[11.615295,60.603483],[11.638641,60.612921],'
                      '[11.6819,60.613258],[11.697693,60.601797],[11.712112,60.586622],[11.703873,60.574476],'
                      '[11.67984,60.568064],[11.640015,60.576838],[11.611862,60.587296]]}'),
            'owner': self.user1.id,
        }
        self.note = {
            'owner': 1,
            'content': 'Are er kul',
            'name': 'Best note ever'
        }
        self.item_list = {
            'name': 'Test list',
            'items': [
                'item one',
                'item two',
                'item three'
            ],
            'items_checked': [
                'item four',
                'item five'
            ],
            'owner': self.user1.id,
            'type': 'check'
        }
        self.trip = {
            'name': 'UTrippin?',
            'owner': self.user1.id,
        }

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user1.email, 'password': 'test'}),
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
        db.destroy()

    def test_create_trip_ok(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], self.user1.id)

    def test_create_trip_add_note(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create note
        response = self.client.post('/note', data=json.dumps(self.note), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        # Add note to trip
        response = self.client.patch(
            '/trip/note', data=json.dumps({'trip_id': trip_id, 'note_id': note_id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trip/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['notes'], [note_id])

    def test_create_trip_add_route(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create route
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        route_id = data['id']

        # Add route to trip
        response = self.client.patch(
            '/trip/route', data=json.dumps({'trip_id': trip_id, 'route_id': route_id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trip/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['routes'], [route_id])

    def test_create_trip_add_item_list(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create item_list
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        item_list_id = data['id']

        # Add item_list to trip
        response = self.client.patch(
            '/trip/item_list',
            data=json.dumps({'trip_id': trip_id, 'item_list_id': item_list_id}),
            headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trip/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['item_lists'], [item_list_id])

    def test_change_trip_owner(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f'/trip/{data["id"]}/owner',
                                     data=json.dumps({'owner': self.user2.id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/trip/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['trip']['owner'], self.user2.id)
