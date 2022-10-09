import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class TripsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'INFO',
            'CREATE_ADMIN_USER': True
        }

        cls.app = create_app(config)
        cls.client = cls.app.test_client()

        cls.user1 = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )
        cls.user2 = User.create(
            User(
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )
        cls.route = {
            'route': ('{\"type\":\"LineString\",\"coordinates\":[[11.615295,60.603483],[11.638641,60.612921],'
                      '[11.6819,60.613258],[11.697693,60.601797],[11.712112,60.586622],[11.703873,60.574476],'
                      '[11.67984,60.568064],[11.640015,60.576838],[11.611862,60.587296]]}'),
            'owner': cls.user1.id,
        }
        cls.note = {
            'owner': cls.user1.id,
            'content': 'Are er kul',
            'name': 'Best note ever'
        }
        cls.item_list = {
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
            'owner': cls.user1.id,
            'type': 'check'
        }
        cls.trip = {
            'name': 'UTrippin?',
            'owner': cls.user1.id,
        }
        cls.trip2 = {
            'name': 'Petter b trippin',
            'owner': cls.user1.id,
        }

        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user1.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'}
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json = {
            'Content-type': 'application/json',
            'Authorization': f'Bearer {data["token"]}'
        }
        cls.headers = {
            'Authorization': f'Bearer {data["token"]}'
        }

    def tearDown(self):
        db.truncate_table('trips')
        db.truncate_table('routes')
        db.truncate_table('item_lists')
        db.truncate_table('lists_items')
        db.truncate_table('notes')
        db.truncate_table('trips_notes_references')
        db.truncate_table('trips_routes_references')
        db.truncate_table('trips_item_lists_references')

    @classmethod
    def tearDownClass(cls):
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

    def test_get_my_trips(self):
        response = self.client.post('/trip', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/trip', data=json.dumps(self.trip2), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('trip/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['count'], 2)
        self.assertEqual(data['trip'][0]['owner'], self.user1.id)
        self.assertEqual(data['trip'][0]['name'], self.trip['name'])
        self.assertEqual(data['trip'][1]['owner'], self.user1.id)
        self.assertEqual(data['trip'][1]['name'], self.trip2['name'])
