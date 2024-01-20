import json
import unittest
from datetime import datetime, timedelta

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
        }
        cls.note = {
            'content': 'Are er kul',
            'name': 'Best note ever'
        }
        cls.item_list = {
            'name': 'Test list',
            'items': [
                {'content': 'item one'},
                {'content': 'item two'},
                {'content': 'item three'}
            ],
            'items_checked': [
                {'content': 'item four'},
                {'content': 'item five'}
            ],
        }
        cls.trip = {
            'name': 'UTrippin?',
        }
        cls.trip2 = {
            'name': 'Petter b trippin',
        }
        cls.trip_with_date = {
            'name': 'where u trippin',
            'dates': [
                {
                    'start_time': datetime.now().isoformat(),
                    'end_time': (datetime.now() + timedelta(minutes=5)).isoformat()
                }
            ]
        }
        cls.trip_with_multiple_dates = {
            'name': 'trippin pete',
            'dates': [
                {
                    'start_time': datetime.now().isoformat(),
                    'end_time': (datetime.now() + timedelta(minutes=10)).isoformat()
                },
                {
                    'start_time': (datetime.now() + timedelta(days=5)).isoformat(),
                    'end_time': (datetime.now() + timedelta(days=8)).isoformat()
                }
            ]
        }
        cls.trip_with_multiple_dates_one_selected = {
            'name': 'trippin pete',
            'dates': [
                {
                    'start_time': datetime.now().isoformat(),
                    'end_time': (datetime.now() + timedelta(minutes=10)).isoformat(),
                    'selected': True
                },
                {
                    'start_time': (datetime.now() + timedelta(days=5)).isoformat(),
                    'end_time': (datetime.now() + timedelta(days=8)).isoformat()
                }
            ]
        }
        cls.trip_with_invalid_date = {
            'name': 'no trip for u',
            'dates': [
                {
                    'start_time': datetime.now().isoformat(),
                    'end_time': (datetime.now() - timedelta(minutes=5)).isoformat()
                }
            ]
        }
        cls.trip_with_date_no_start = {
            'name': 'no trip for u2',
            'dates': [
                {
                    'end_time': (datetime.now() - timedelta(minutes=5)).isoformat()
                }
            ]
        }
        cls.trip_with_date_no_end = {
            'name': 'no trip for u3',
            'dates': [
                {
                    'start_time': datetime.now().isoformat(),
                }
            ]
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
        db.truncate_table('trip_dates')
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
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], self.user1.id)

    def test_delete_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        response = self.client.delete(f'/trips/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/trips/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Trip not found')
        self.assertEqual(data['detail'], 'The requested trip was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{id}')

    def test_create_trip_add_note(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create note
        response = self.client.post('/notes', data=json.dumps(self.note), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        # Add note to trip
        response = self.client.patch(
            '/trips/notes', data=json.dumps({'trip_id': trip_id, 'note_id': note_id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trips/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['notes'], [note_id])

    def test_create_trip_add_route(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create route
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        route_id = data['id']

        # Add route to trip
        response = self.client.patch(
            '/trips/routes', data=json.dumps({'trip_id': trip_id, 'route_id': route_id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trips/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['routes'], [route_id])

    def test_create_trip_add_item_list(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        # Create item_list
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        item_list_id = data['id']

        # Add item_list to trip
        response = self.client.patch(
            '/trips/item_lists',
            data=json.dumps({'trip_id': trip_id, 'item_list_id': item_list_id}),
            headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/trips/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['item_lists'], [item_list_id])

    def test_change_trip_owner(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)

        response = self.client.patch(f'/trips/{data["id"]}/owner',
                                     data=json.dumps({'owner': self.user2.id}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/trips/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['trip']['owner'], self.user2.id)

    def test_get_my_trips(self):
        response = self.client.post('/trips', data=json.dumps(self.trip), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/trips', data=json.dumps(self.trip2), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/trips', data=json.dumps(self.trip_with_date), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/trips/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['count'], 3)
        self.assertEqual(data['trip'][0]['owner'], self.user1.id)
        self.assertEqual(data['trip'][0]['name'], self.trip['name'])
        self.assertEqual(data['trip'][1]['owner'], self.user1.id)
        self.assertEqual(data['trip'][1]['name'], self.trip2['name'])

        self.assertEqual(data['trip'][2]['name'], self.trip_with_date['name'])
        self.assertEqual(data['trip'][2]['owner'], data['trip'][2]['dates'][0]['owner'])
        self.assertEqual(data['trip'][2]['dates'][0]['trip_id'], 3)
        self.assertEqual(data['trip'][2]['id'], data['trip'][2]['dates'][0]['trip_id'])
        self.assertEqual(data['trip'][2]['dates'][0]['start_time'], self.trip_with_date['dates'][0]['start_time'])
        self.assertEqual(data['trip'][2]['dates'][0]['end_time'], self.trip_with_date['dates'][0]['end_time'])
        self.assertEqual(data['trip'][2]['owner'], self.user1.id)

    def test_create_trip_with_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_date),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['name'], self.trip_with_date['name'])
        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['trip_id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['start_time'], self.trip_with_date['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], self.trip_with_date['dates'][0]['end_time'])
        self.assertEqual(data['owner'], self.user1.id)

    def test_create_trip_with_multiple_dates(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(data['name'], self.trip_with_multiple_dates['name'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['start_time'], self.trip_with_multiple_dates['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], self.trip_with_multiple_dates['dates'][0]['end_time'])

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['start_time'], self.trip_with_multiple_dates['dates'][1]['start_time'])
        self.assertEqual(data['dates'][1]['end_time'], self.trip_with_multiple_dates['dates'][1]['end_time'])

    def test_create_trip_with_multiple_dates_one_selected(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates_one_selected),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(data['name'], self.trip_with_multiple_dates_one_selected['name'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], True)
        self.assertEqual(
            data['dates'][0]['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['start_time']
        )
        self.assertEqual(
            data['dates'][0]['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['end_time']
        )

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['selected'], False)
        self.assertEqual(
            data['dates'][1]['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['start_time']
        )
        self.assertEqual(
            data['dates'][1]['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['end_time']
        )

    def test_create_trip_with_invalid_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_invalid_date),
            headers=self.headers_json
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_date_no_start),
            headers=self.headers_json
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_date_no_end),
            headers=self.headers_json
        )
        self.assertEqual(response.status_code, 400)

    def test_add_date_to_trip(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_date),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], self.trip_with_date['name'])
        self.assertEqual(data['owner'], self.user1.id)

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['trip_id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['start_time'], self.trip_with_date['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], self.trip_with_date['dates'][0]['end_time'])

        start_time = (datetime.now() + timedelta(days=7)).isoformat()
        end_time = (datetime.now() + timedelta(days=14)).isoformat()
        response = self.client.patch(
            f'/trips/{id}/dates',
            data=json.dumps(
                {
                    'start_time': start_time,
                    'end_time': end_time,
                }
            ),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['trip_id'], id)
        self.assertEqual(data['owner'], self.user1.id)

        response = self.client.get(
            f'/trips/{id}',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['id'], 1)
        self.assertEqual(data['trip']['name'], self.trip_with_date['name'])
        self.assertEqual(data['trip']['owner'], data['trip']['dates'][0]['owner'])
        self.assertEqual(data['trip']['dates'][0]['trip_id'], 1)
        self.assertEqual(data['trip']['id'], data['trip']['dates'][0]['trip_id'])
        self.assertEqual(len(data['trip']['dates']), 2)
        self.assertEqual(data['trip']['dates'][0]['start_time'], self.trip_with_date['dates'][0]['start_time'])
        self.assertEqual(data['trip']['dates'][0]['end_time'], self.trip_with_date['dates'][0]['end_time'])
        self.assertEqual(data['trip']['dates'][1]['start_time'], start_time)
        self.assertEqual(data['trip']['dates'][1]['end_time'], end_time)
        self.assertEqual(data['trip']['owner'], self.user1.id)

    def test_remove_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']
        date_id = data['dates'][0]['id']

        response = self.client.delete(
            f'/trips/{trip_id}/dates/{date_id}',
            headers=self.headers
        )

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/trips/{trip_id}',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['trip']['id'], 1)
        self.assertEqual(data['trip']['name'], self.trip_with_multiple_dates['name'])
        self.assertEqual(len(data['trip']['dates']), 1)
        self.assertEqual(data['trip']['dates'][0]['owner'], data['trip']['owner'])
        self.assertEqual(data['trip']['dates'][0]['id'], 2)
        self.assertEqual(data['trip']['dates'][0]['trip_id'], 1)
        self.assertEqual(data['trip']['dates'][0]['trip_id'], data['trip']['id'])
        self.assertEqual(
            data['trip']['dates'][0]['start_time'],
            self.trip_with_multiple_dates['dates'][1]['start_time']
        )
        self.assertEqual(
            data['trip']['dates'][0]['end_time'],
            self.trip_with_multiple_dates['dates'][1]['end_time']
        )
        self.assertEqual(data['trip']['owner'], self.user1.id)

    def test_select_trip_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']
        date_id = data['dates'][0]['id']


        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(data['name'], self.trip_with_multiple_dates['name'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], False)
        self.assertEqual(
            data['dates'][0]['start_time'],
            self.trip_with_multiple_dates['dates'][0]['start_time']
        )
        self.assertEqual(
            data['dates'][0]['end_time'],
            self.trip_with_multiple_dates['dates'][0]['end_time']
        )

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], False)
        self.assertEqual(
            data['dates'][1]['start_time'],
            self.trip_with_multiple_dates['dates'][1]['start_time']
        )
        self.assertEqual(
            data['dates'][1]['end_time'],
            self.trip_with_multiple_dates['dates'][1]['end_time']
        )

        response = self.client.patch(
            f'/trips/{trip_id}/dates/{date_id}/select',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/trips/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))


        for date in data['trip']['dates']:
            if date['selected'] is True:
                data_date = date
                break

        self.assertEqual(data_date['owner'], data['trip']['owner'])
        self.assertEqual(data_date['id'], 1)
        self.assertEqual(data_date['trip_id'], data['trip']['id'])
        self.assertEqual(data_date['selected'], True)
        self.assertEqual(data_date['start_time'], self.trip_with_multiple_dates['dates'][0]['start_time'])
        self.assertEqual(data_date['end_time'], self.trip_with_multiple_dates['dates'][0]['end_time'])

    def test_create_with_selected_select_new_trip_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates_one_selected),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']
        date_id = data['dates'][1]['id']


        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(data['name'], self.trip_with_multiple_dates_one_selected['name'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], True)
        self.assertEqual(
            data['dates'][0]['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['start_time']
        )
        self.assertEqual(
            data['dates'][0]['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['end_time']
        )

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['selected'], False)
        self.assertEqual(
            data['dates'][1]['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['start_time']
        )
        self.assertEqual(
            data['dates'][1]['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['end_time']
        )

        response = self.client.patch(
            f'/trips/{trip_id}/dates/{date_id}/select',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/trips/{trip_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        for date in data['trip']['dates']:
            if date['selected'] is True:
                selected_date = date
                continue
            if date['selected'] is False:
                unselected_date = date
                continue

        self.assertEqual(selected_date['owner'], data['trip']['owner'])
        self.assertEqual(selected_date['id'], 2)
        self.assertEqual(selected_date['trip_id'], data['trip']['id'])
        self.assertEqual(selected_date['selected'], True)
        self.assertEqual(
            selected_date['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['start_time']
        )
        self.assertEqual(
            selected_date['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][1]['end_time']
        )

        self.assertEqual(unselected_date['owner'], data['trip']['owner'])
        self.assertEqual(unselected_date['id'], 1)
        self.assertEqual(unselected_date['trip_id'], data['trip']['id'])
        self.assertEqual(unselected_date['selected'], False)
        self.assertEqual(
            unselected_date['start_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['start_time']
        )
        self.assertEqual(
            unselected_date['end_time'],
            self.trip_with_multiple_dates_one_selected['dates'][0]['end_time']
        )


    def test_update_trip_name(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates_one_selected),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        trip = json.loads(response.data.decode('utf-8'))

        trip['name'] = 'New tripin pete'

        response = self.client.put(
            f'/trips/{trip["id"]}',
            data=json.dumps(trip),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], trip['id'])
        self.assertEqual(data['owner'], trip['owner'])
        self.assertEqual(data['name'], trip['name'])

        self.assertCountEqual(data['dates'], trip['dates'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], True)
        self.assertEqual(data['dates'][0]['start_time'], trip['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], trip['dates'][0]['end_time'])

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['selected'], False)
        self.assertEqual(data['dates'][1]['start_time'], trip['dates'][1]['start_time'])
        self.assertEqual(data['dates'][1]['end_time'], trip['dates'][1]['end_time'])


    def test_update_trip_add_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        trip = json.loads(response.data.decode('utf-8'))

        trip['dates'].append(
            {
                'start_time': (datetime.now() + timedelta(days=7)).isoformat(),
                'end_time': (datetime.now() + timedelta(days=8)).isoformat()
            }
        )

        response = self.client.put(
            f'/trips/{trip["id"]}',
            data=json.dumps(trip),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['id'], trip['id'])
        self.assertEqual(data['owner'], trip['owner'])
        self.assertEqual(data['name'], trip['name'])

        self.assertEqual(len(data['dates']), len(trip['dates']))

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], False)
        self.assertEqual(data['dates'][0]['start_time'], trip['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], trip['dates'][0]['end_time'])

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['selected'], False)
        self.assertEqual(data['dates'][1]['start_time'], trip['dates'][1]['start_time'])
        self.assertEqual(data['dates'][1]['end_time'], trip['dates'][1]['end_time'])

        self.assertEqual(data['dates'][2]['owner'], data['owner'])
        self.assertEqual(data['dates'][2]['id'], 3)
        self.assertEqual(data['dates'][2]['trip_id'], data['id'])
        self.assertEqual(data['dates'][2]['selected'], False)
        self.assertEqual(data['dates'][2]['start_time'], trip['dates'][2]['start_time'])
        self.assertEqual(data['dates'][2]['end_time'], trip['dates'][2]['end_time'])

    def test_update_trip_remove_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        trip = json.loads(response.data.decode('utf-8'))

        trip['dates'].pop(1)

        response = self.client.put(
            f'/trips/{trip["id"]}',
            data=json.dumps(trip),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['id'], trip['id'])
        self.assertEqual(data['owner'], trip['owner'])
        self.assertEqual(data['name'], trip['name'])

        self.assertCountEqual(data['dates'], trip['dates'])

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], False)
        self.assertEqual(data['dates'][0]['start_time'], trip['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], trip['dates'][0]['end_time'])

    def test_update_trip_change_date(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        trip = json.loads(response.data.decode('utf-8'))

        trip['dates'][0]['end_time'] = (datetime.now() + timedelta(days=8)).isoformat()

        response = self.client.put(
            f'/trips/{trip["id"]}',
            data=json.dumps(trip),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], trip['id'])
        self.assertEqual(data['owner'], trip['owner'])
        self.assertEqual(data['name'], trip['name'])

        self.assertEqual(len(data['dates']), len(trip['dates']))

        self.assertEqual(data['dates'][0]['owner'], data['owner'])
        self.assertEqual(data['dates'][0]['id'], 1)
        self.assertEqual(data['dates'][0]['trip_id'], data['id'])
        self.assertEqual(data['dates'][0]['selected'], False)
        self.assertEqual(data['dates'][0]['start_time'], trip['dates'][0]['start_time'])
        self.assertEqual(data['dates'][0]['end_time'], trip['dates'][0]['end_time'])

        self.assertEqual(data['dates'][1]['owner'], data['owner'])
        self.assertEqual(data['dates'][1]['id'], 2)
        self.assertEqual(data['dates'][1]['trip_id'], data['id'])
        self.assertEqual(data['dates'][1]['selected'], False)
        self.assertEqual(data['dates'][1]['start_time'], trip['dates'][1]['start_time'])
        self.assertEqual(data['dates'][1]['end_time'], trip['dates'][1]['end_time'])

    def test_update_trip_no_change(self):
        response = self.client.post(
            '/trips',
            data=json.dumps(self.trip_with_multiple_dates),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        trip = json.loads(response.data.decode('utf-8'))

        response = self.client.put(
            f'/trips/{trip["id"]}',
            data=json.dumps(trip),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 400)
