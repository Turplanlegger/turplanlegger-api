import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'LOG_LEVEL': 'INFO'
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        self.user1 = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no',
            'auth_method': 'basic',
            'password': 'test123',
            'private': False
        }
        self.user2 = {
            'name': 'Kari',
            'email': 'kari.nordmann@norge.no',
            'auth_method': 'basic',
            'password': 'test123',
            'private': False
        }
        self.user3 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'invalid.com',
            'auth_method': 'basic',
            'password': 'test123',
            'private': False
        }
        self.user4 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': 'te',
            'private': True
        }
        self.user5 = {
            'name': 'Ørulf',
            'last_name': 'Åsenæs',
            'email': 'oernulf.aasenaes@norge.no',
            'auth_method': 'basic',
            'password': 'test123',
            'private': True
        }
        self.user6 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': 'GbYRCzE}q:~e6Qo?\':fg^*:d6;{*NV&b=Q2GUAqYv#792C<{?,8@JoYX>qV)3H^q',
            'private': False
        }
        self.user7 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': 'm9uMSpb&q.Ft,[5,%oWj7yk-$YFBvKd}J<fNrToR2x~&+d_9J}K:gcGmUq#qkL\'#',
            'private': False
        }
        self.user8 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': ('TZULjwxS3K5MPZv8P4qz3KfsEnxjCsZgd7HNWFXkhcutEDMxzcU5HyEv2'
                         'VVm9okEaF5tjDfpoqyZrYwVfbQicrvNQrpjqxYexihKVUvJxN23LJxAvf'
                         'vbbAsU2mbUw67b'),
            'private': False
        }
        self.user9 = {
            'name': 'Péter',
            'last_name': 'Smart',
            'email': 'peter@smart.com',
            'auth_method': 'basic',
            'password': ('>Q`CV"%3c9naU3(fj@eX~N,7+Qx~_t[+Nt9R4~7m(YRK/r)n!T;onA,^G7F'
                         '+7]<uqy#xGmWkoaN4.JhxK!}u-S4#y^aC"dfBThL^w\'Y2M(qPyr(prX[Vc'
                         'r_P~:v]Vbc;'),
            'private': False
        }
        self.user10 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': 'JegErEtPassordeSomBurdeFunkeDaVelÅsåæSø',
            'private': False
        }
        self.user11 = {
            'name': 'Petter',
            'last_name': 'Smart',
            'email': 'petter@smart.com',
            'auth_method': 'basic',
            'password': 'JegErEtPassordeSomBurdeFunkeDaVelÅsåæSø',
            'private': True
        }

        self.test_user = User.create(
            User(
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.test_user.email, 'password': 'test'}),
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

    def test_user_not_found(self):
        response = self.client.get('/user/3', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'User not found')
        self.assertEqual(data['detail'], 'The requested user was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/user/3')

    def test_create_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user1['name'])
        self.assertEqual(data['user']['last_name'], self.user1['last_name'])
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], self.user1['private'])

    def test_create_private_user(self):
        response = self.client.post('/user', data=json.dumps(self.user11), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user11['name'])
        self.assertEqual(data['user']['last_name'], self.user11['last_name'])
        self.assertEqual(data['user']['email'], self.user11['email'])
        self.assertEqual(data['user']['auth_method'], self.user11['auth_method'])
        self.assertEqual(data['user']['private'], self.user11['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user11['email'], 'password': self.user11['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        response = self.client.delete(f'/user/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/user/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'User not found')
        self.assertEqual(data['detail'], 'The requested user was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/user/{id}')

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user1['email'], 'password': self.user1['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_user_no_last_name(self):
        response = self.client.post('/user', data=json.dumps(self.user2), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse user')
        self.assertEqual(data['detail'], 'Missing mandatory field \'last_name\'')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/user')

    def test_create_user_invalid_email(self):
        response = self.client.post('/user', data=json.dumps(self.user3), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse user')
        self.assertEqual(data['detail'], 'Invalid email address')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/user')

    def test_rename_user(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            f'/user/{data["id"]}/rename',
            data=json.dumps({'name': 'Petter', 'last_name': 'Smart'}),
            headers=self.headers_json
        )
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user']['name'], 'Petter')
        self.assertEqual(data['user']['last_name'], 'Smart')
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], self.user1['private'])

    def test_change_private(self):
        response = self.client.post('/user', data=json.dumps(self.user1), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f'/user/{data["id"]}/private', headers=self.headers)

        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/user/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['user']['name'], self.user1['name'])
        self.assertEqual(data['user']['last_name'], self.user1['last_name'])
        self.assertEqual(data['user']['email'], self.user1['email'])
        self.assertEqual(data['user']['auth_method'], self.user1['auth_method'])
        self.assertEqual(data['user']['private'], True)

    def test_create_user_short_pw(self):
        response = self.client.post('/user', data=json.dumps(self.user4), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse user')
        self.assertEqual(data['detail'], 'Password too short')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/user')

    def test_create_special_char(self):
        response = self.client.post('/user', data=json.dumps(self.user5), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user5['name'])
        self.assertEqual(data['user']['last_name'], self.user5['last_name'])
        self.assertEqual(data['user']['email'], self.user5['email'])
        self.assertEqual(data['user']['auth_method'], self.user5['auth_method'])
        self.assertEqual(data['user']['private'], self.user5['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user5['email'], 'password': self.user5['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_create_special_char2(self):
        response = self.client.post('/user', data=json.dumps(self.user9), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user9['name'])
        self.assertEqual(data['user']['last_name'], self.user9['last_name'])
        self.assertEqual(data['user']['email'], self.user9['email'])
        self.assertEqual(data['user']['auth_method'], self.user9['auth_method'])
        self.assertEqual(data['user']['private'], self.user9['private'])

    def test_create_user_long_pw1(self):
        response = self.client.post('/user', data=json.dumps(self.user6), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user6['name'])
        self.assertEqual(data['user']['last_name'], self.user6['last_name'])
        self.assertEqual(data['user']['email'], self.user6['email'])
        self.assertEqual(data['user']['auth_method'], self.user6['auth_method'])
        self.assertEqual(data['user']['private'], self.user6['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user6['email'], 'password': self.user6['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_create_user_long_pw2(self):
        response = self.client.post('/user', data=json.dumps(self.user7), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user7['name'])
        self.assertEqual(data['user']['last_name'], self.user7['last_name'])
        self.assertEqual(data['user']['email'], self.user7['email'])
        self.assertEqual(data['user']['auth_method'], self.user7['auth_method'])
        self.assertEqual(data['user']['private'], self.user7['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user7['email'], 'password': self.user7['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_create_user_long_pw3(self):
        response = self.client.post('/user', data=json.dumps(self.user8), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user8['name'])
        self.assertEqual(data['user']['last_name'], self.user8['last_name'])
        self.assertEqual(data['user']['email'], self.user8['email'])
        self.assertEqual(data['user']['auth_method'], self.user8['auth_method'])
        self.assertEqual(data['user']['private'], self.user8['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user8['email'], 'password': self.user8['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_create_user_long_pw4(self):
        response = self.client.post('/user', data=json.dumps(self.user9), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user9['name'])
        self.assertEqual(data['user']['last_name'], self.user9['last_name'])
        self.assertEqual(data['user']['email'], self.user9['email'])
        self.assertEqual(data['user']['auth_method'], self.user9['auth_method'])
        self.assertEqual(data['user']['private'], self.user9['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user9['email'], 'password': self.user9['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_create_user_long_pw5(self):
        response = self.client.post('/user', data=json.dumps(self.user10), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['user']['name'], self.user10['name'])
        self.assertEqual(data['user']['last_name'], self.user10['last_name'])
        self.assertEqual(data['user']['email'], self.user10['email'])
        self.assertEqual(data['user']['auth_method'], self.user10['auth_method'])
        self.assertEqual(data['user']['private'], self.user10['private'])

        response = self.client.post(
            '/login',
            data=json.dumps({'email': self.user10['email'], 'password': self.user10['password']}),
            headers={'Content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        response = self.client.get('/user/2', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)
