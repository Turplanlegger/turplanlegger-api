import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class NotesTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'LOG_LEVEL': 'INFO'
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

        self.note_full = {
            'owner': 1,
            'content': 'Are er kul',
            'name': 'Best note ever'
        }
        self.note_no_name = {
            'owner': 1,
            'content': 'Are er kul',
        }
        self.note_no_content = {
            'owner': 1,
            'name': 'Best note ever',
        }
        self.note_no_owner = {
            'content': 'Are er kul',
            'name': 'Best note ever'
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

    def test_add_note_ok(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], 1)
        self.assertEqual(data['content'], 'Are er kul')
        self.assertEqual(data['name'], 'Best note ever')

    def test_add_note_no_owner(self):
        response = self.client.post('/note', data=json.dumps(self.note_no_owner), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse note')
        self.assertEqual(data['detail'], 'Missing mandatory field \'owner\'')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/note')

    def test_get_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/note/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], self.note_full['owner'])
        self.assertEqual(data['note']['content'], self.note_full['content'])
        self.assertEqual(data['note']['name'], self.note_full['name'])

    def test_get_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/note/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/note/2')

    def test_delete_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        response = self.client.delete(f'/note/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/note/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/note/{id}')

    def test_delete_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('/note/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/note/2')

    def test_change_note_owner(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f'/note/{data["id"]}/owner',
                                     data=json.dumps({'owner': 2}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/note/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], 2)

    def test_change_note_owner_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/2/owner', data=json.dumps({'owner': 2}), headers=self.headers_json)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/note/2/owner')

    def test_change_note_owner_no_owner_given(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/1/owner', data=json.dumps({}), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Owner is not int')
        self.assertEqual(data['detail'], 'Owner must be passed as an int')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/note/1/owner')

    def test_rename_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/1/rename', data=json.dumps({'name': 'newlist'}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')

    def test_update_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            '/note/1/update', data=json.dumps({'content': 'newcontent'}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')
