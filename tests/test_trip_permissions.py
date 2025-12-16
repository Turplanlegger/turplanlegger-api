import json
import unittest
from datetime import UTC, datetime, timedelta

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class TripsPermissionsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        cls.user1 = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )
        cls.user2 = User.create(
            User(
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

        cls.trip_read = {
            'name': 'trippin pete perms',
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.trip_read_private = {
            'name': 'trippin pete perms',
            'private': True,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.trip_modify = {
            'name': 'trippin pete perms',
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.trip_modify_private = {
            'name': 'trippin pete perms',
            'private': True,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.trip_delete = {
            'name': 'trippin pete perms',
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
        db.truncate_table('trips')
        db.truncate_table('trip_permissions')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_create_trip_with_permissions_ok(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['owner'], str(self.user1.id))
        self.assertEqual(data['name'], self.trip_read['name'])
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['permissions'][0]['object_id'], data['id'])
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

    def test_get_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

        # User 2 - ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['trip']['permissions']), 1)
        self.assertEqual(data['trip']['permissions'][0]['subject_id'], str(self.user2.id))

        # User 3 - ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user3)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

    def test_get_private_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read_private), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

        # User 2 - ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['trip']['permissions']), 1)
        self.assertEqual(data['trip']['permissions'][0]['subject_id'], str(self.user2.id))

        # User 3 - not ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Trip not found')
        self.assertEqual(data['detail'], 'The requested trip was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{trip_id}')

    def test_update_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_modify), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        trip = json.loads(response.data.decode('utf-8'))
        trip['name'] = 'Tripper'
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': trip.get('name')}), headers=self.headers_json_user1
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('trip'), trip)

        # User 2 - ok
        response = self.client.get(f'/trips/{trip["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        trip['name'] = 'Tripper2'
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': trip.get('name')}), headers=self.headers_json_user2
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('trip'), trip)

        response = self.client.get(f'/trips/{trip["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        # User 3 - not ok
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': 'poopy'}), headers=self.headers_json_user3
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 403)

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to modify the trip')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{trip["id"]}')

    def test_update_private_trip(self):
        response = self.client.post(
            '/trips', data=json.dumps(self.trip_modify_private), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 201)
        trip = json.loads(response.data.decode('utf-8'))
        trip['name'] = 'Tripper'
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': trip.get('name')}), headers=self.headers_json_user1
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('trip'), trip)

        # User 2 - ok
        response = self.client.get(f'/trips/{trip["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        trip['name'] = 'Tripper2'
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': trip.get('name')}), headers=self.headers_json_user2
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('trip'), trip)

        response = self.client.get(f'/trips/{trip["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        # User 3 - not ok
        response = self.client.put(
            f'/trips/{trip["id"]}', data=json.dumps({'name': 'poopy'}), headers=self.headers_json_user3
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

        self.assertEqual(data['title'], 'Trip not found')
        self.assertEqual(data['detail'], 'The requested trip was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{trip["id"]}')

    def test_delete_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_delete), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        trip = json.loads(response.data.decode('utf-8'))
        response = self.client.delete(f'/trips/{trip["id"]}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        # User 2 - ok
        response = self.client.post('/trips', data=json.dumps(self.trip_delete), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        trip = json.loads(response.data.decode('utf-8'))
        response = self.client.delete(f'/trips/{trip["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        # User 3 - not ok
        response = self.client.post('/trips', data=json.dumps(self.trip_delete), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        trip = json.loads(response.data.decode('utf-8'))

        response = self.client.delete(f'/trips/{trip["id"]}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to delete the trip')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{trip["id"]}')

    def test_update_trip_with_read(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        # User 2
        ## Ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        ## Not ok
        response = self.client.put(
            f'/trips/{id}', data=json.dumps({'name': 'Tripper2'}), headers=self.headers_json_user2
        )

        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to modify the trip')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{id}')

    def test_change_trip_owner(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        # User 1 -> user 2
        ## Ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        response = self.client.get(f'/trips/{id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        ## Ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        ## Ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 200)

        # User 1 -> user 3
        ## Not ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user3.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change ownership the trip')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{id}/owner')

        # User 2 -> user 3
        ## Ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user3.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f'/trips/{id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        ## Ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        ## Ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 200)

        # User 3 -> user 2
        ## Not ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user3.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

    def test_change_trip_owner_private(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read_private), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        # User 1 -> user 2
        ## Ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        response = self.client.get(f'/trips/{id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        ## Not ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Trip not found')
        self.assertEqual(data['detail'], 'The requested trip was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/trips/{id}')

        # User 1 -> user 3
        ## Not ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user3.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        # User 2 -> user 3
        ## Ok
        response = self.client.patch(
            f'/trips/{id}/owner', data=json.dumps({'owner': str(self.user3.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f'/trips/{id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        ## Not ok
        response = self.client.get(f'/trips/{id}', headers=self.headers_user1)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def test_delete_trip_read(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read), headers=self.headers_json_user1)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        for user in (self.headers_user2, self.headers_user3):
            response = self.client.delete(f'/trips/{trip_id}', headers=user)
            self.assertEqual(response.status_code, 403)

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        for user in (self.headers_user1, self.headers_user2, self.headers_user3):
            response = self.client.delete(f'/trips/{trip_id}', headers=user)
            self.assertEqual(response.status_code, 404)

    def test_delete_trip_private(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read_private), headers=self.headers_json_user1)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        for user in (self.headers_user1, self.headers_user2, self.headers_user3):
            response = self.client.delete(f'/trips/{trip_id}', headers=user)
            self.assertEqual(response.status_code, 404)

    def test_delete_trip_modify(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_modify), headers=self.headers_json_user1)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        for user in (self.headers_user2, self.headers_user3):
            response = self.client.delete(f'/trips/{trip_id}', headers=user)
            self.assertEqual(response.status_code, 403)

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)

        for user in (self.headers_user1, self.headers_user2, self.headers_user3):
            response = self.client.delete(f'/trips/{trip_id}', headers=user)
            self.assertEqual(response.status_code, 404)

    def test_delete_trip_delete(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_delete), headers=self.headers_json_user1)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

    def test_add_date_to_trip(self):
        response = self.client.post('/trips', data=json.dumps(self.trip_read_private), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        trip_id = data['id']

        start_time = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end_time = (datetime.now(UTC) + timedelta(days=14)).isoformat()

        # User 2
        # Ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['trip']['dates']), 0)

        # Not ok
        response = self.client.patch(
            f'/trips/{trip_id}/dates',
            data=json.dumps(
                {
                    'start_time': start_time,
                    'end_time': end_time,
                }
            ),
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 403)

        # Ok
        # User 3
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)

        # Not ok
        response = self.client.patch(
            f'/trips/{trip_id}/dates',
            data=json.dumps(
                {
                    'start_time': start_time,
                    'end_time': end_time,
                }
            ),
            headers=self.headers_json_user3,
        )

        # Not ok
        self.assertEqual(response.status_code, 404)

        response = self.client.get(f'/trips/{id}', headers=self.headers_user1)

        # User 1
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['trip']['dates']), 0)

        response = self.client.patch(
            f'/trips/{trip_id}/dates',
            data=json.dumps(
                {
                    'start_time': start_time,
                    'end_time': end_time,
                }
            ),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 201)

        # User 2
        # Ok
        response = self.client.get(f'/trips/{trip_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['trip']['dates']), 1)
