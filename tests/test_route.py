import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.models.user import User


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        self.user1 = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic'
            )
        )
        self.user2 = User.create(
            User(
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic'
            )
        )

        routeGeometry = ('{\"type\":\"LineString\",\"coordinates\":[[11.615295,60.603483],[11.638641,60.612921],'
                         '[11.6819,60.613258],[11.697693,60.601797],[11.712112,60.586622],[11.703873,60.574476],'
                         '[11.67984,60.568064],[11.640015,60.576838],[11.611862,60.587296]]}')
        self.route = {
            'route': routeGeometry,
            'owner': self.user1.id,
        }
        self.route_no_owner = {
            'route': routeGeometry,
        }
        self.route_no_geometry = {
            'owner': self.user1.id,
        }
        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):
        db.destroy()

    def test_add_route_ok(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], 1)

    def test_add_route_no_owner(self):
        response = self.client.post('/route', data=json.dumps(self.route_no_owner), headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Missing mandatory field "owner"')

    def test_add_route_no_geometry(self):
        response = self.client.post('/route', data=json.dumps(self.route_no_geometry), headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Missing mandatory field "route"')

    def test_get_route(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.get(f'/route/{created_route_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['route']['owner'], self.route['owner'])

    def test_get_route_not_found(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/route/2')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'route not found')

    def test_delete_route(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.delete(f'/route/{created_route_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_route_not_found(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('/route/2')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'route not found')

    def test_change_route_owner(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.patch(
            f'/route/{created_route_id}/owner',
            data=json.dumps({'owner': self.user2.id}),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/route/{created_route_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['route']['owner'], self.user2.id)

    def test_change_route_owner_route_not_found(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            '/route/2/owner',
            data=json.dumps({'owner': self.user2.id}),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'route not found')

    def test_change_route_owner_no_owner_given(self):
        response = self.client.post('/route', data=json.dumps(self.route), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/route/1/owner', data=json.dumps({}), headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'must supply owner as int')
