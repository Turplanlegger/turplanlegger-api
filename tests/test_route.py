import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class RoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'INFO',
            'CREATE_ADMIN_USER': True,
        }

        cls.app = create_app(config)
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

        routeGeometry = (
            '{"type":"LineString","coordinates":[[11.615295,60.603483],[11.638641,60.612921],'
            '[11.6819,60.613258],[11.697693,60.601797],[11.712112,60.586622],[11.703873,60.574476],'
            '[11.67984,60.568064],[11.640015,60.576838],[11.611862,60.587296]]}'
        )
        cls.route = {'route': routeGeometry}
        cls.route_no_geometry = {}

        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user1.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )

        if response.status_code != 200:
            raise RuntimeError('Failed to login')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.headers = {'Authorization': f'Bearer {data["token"]}'}

    def tearDown(self):
        db.truncate_table('routes')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_add_route_ok(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], self.user1.id)

    def test_add_route_no_geometry(self):
        response = self.client.post('/routes', data=json.dumps(self.route_no_geometry), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse route')
        self.assertEqual(data['detail'], "Missing mandatory field 'route'")
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/routes')

    def test_get_route(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.get(f'/routes/{created_route_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['route']['owner'], self.user1.id)

    def test_get_route_not_found(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/routes/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Route not found')
        self.assertEqual(data['detail'], 'The requested route was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/routes/2')

    def test_delete_route(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.delete(f'/routes/{created_route_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_delete_route_not_found(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('/routes/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Route not found')
        self.assertEqual(data['detail'], 'The requested route was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/routes/2')

    def test_change_route_owner(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_route_id = data['id']

        response = self.client.patch(
            f'/routes/{created_route_id}/owner', data=json.dumps({'owner': self.user2.id}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/routes/{created_route_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['route']['owner'], self.user2.id)

    def test_change_route_owner_route_not_found(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            '/routes/2/owner', data=json.dumps({'owner': self.user2.id}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Route not found')
        self.assertEqual(data['detail'], 'The requested route was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/routes/2/owner')

    def test_change_route_owner_no_owner_given(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/routes/1/owner', data=json.dumps({}), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Owner is not int')
        self.assertEqual(data['detail'], 'Owner must be passed as an int')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/routes/1/owner')

    def test_get_my_routes(self):
        response = self.client.post('/routes', data=json.dumps(self.route), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/routes/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['route'][0]['owner'], self.user1.id)
