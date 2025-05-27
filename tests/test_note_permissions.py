import json
import unittest
from uuid import uuid4

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class NotesTestCase(unittest.TestCase):
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
                id=str(uuid4()),
                name='Ola',
                last_name='Nordamnn',
                email='old.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )
        cls.user2 = User.create(
            User(
                id=str(uuid4()),
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

        cls.note_no_content = {
            'name': 'Best note ever',
        }
        cls.note_read = {
            'name': 'Notin pete read perms',
            'content': 'Wait a minute, these notes have permissions with them',
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.note_modify = {
            'name': 'Notin pete modify perms',
            'content': 'Wait a minute, these notes have more permissions with them',
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.note_delete = {
            'name': 'Notin pete modify perms',
            'content': 'Wait a minute, these notes have even more permissions with them',
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
        db.truncate_table('notes')
        db.truncate_table('note_permissions')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_add_note_ok(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], str(self.user1.id))
        self.assertEqual(data['content'], self.note_read['content'])
        self.assertEqual(data['name'], self.note_read['name'])
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['permissions'][0]['object_id'], data['id'])
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

    def test_get_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user2.id))

        # User 2 - ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['note']['permissions']), 1)
        self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))

        # User 3 - not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')