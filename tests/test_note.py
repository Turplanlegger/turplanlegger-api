import json
import unittest
from uuid import uuid4

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class NotesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
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

        cls.note_full = {'content': 'Are er kul', 'name': 'Best note ever'}
        cls.note_full2 = {'content': 'Petter er kul', 'name': 'Best note ever'}
        cls.note_no_name = {'content': 'Are er kul'}
        cls.note_no_content = {'name': 'Best note ever'}
        cls.note_blank_content = {'content': '   ', 'name': 'Best note ever'}

        # User 1
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

        # User 2
        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user2.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )
        if response.status_code != 200:
            raise RuntimeError('Failed to login')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json2 = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.headers2 = {'Authorization': f'Bearer {data["token"]}'}

    def tearDown(self):
        db.truncate_table('notes')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_add_note_ok(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], str(self.user1.id))
        self.assertEqual(data['content'], 'Are er kul')
        self.assertEqual(data['name'], 'Best note ever')

    def test_add_note_blank_content(self):
        response = self.client.post('/notes', data=json.dumps(self.note_blank_content), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse note')
        self.assertEqual(data['detail'], "'content' must not be blank")
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes')

    def test_get_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get(f'/notes/{data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], str(self.user1.id))
        self.assertEqual(data['note']['content'], self.note_full['content'])
        self.assertEqual(data['note']['name'], self.note_full['name'])

    def test_get_note_not_found(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/notes/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/2')

    def test_delete_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        id = data['id']

        response = self.client.delete(f'/notes/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/notes/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{id}')

    def test_delete_note_not_found(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('/notes/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/2')

    def test_change_note_owner(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        note = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            f'/notes/{note["id"]}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers2)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], str(self.user2.id))
        self.assertEqual(data['note']['content'], self.note_full['content'])
        self.assertEqual(data['note']['name'], self.note_full['name'])

        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/1')

    def test_change_note_owner_note_not_found(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            '/notes/2/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/2/owner')

    def test_change_note_owner_no_owner_given(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.patch('/notes/1/owner', data=json.dumps({}), headers=self.headers_json)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to change owner')
        self.assertEqual(data['detail'], 'Owner id must be passed as an UUID')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/1/owner')

    def test_rename_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/notes/1/rename', data=json.dumps({'name': 'newlist'}), headers=self.headers_json)
        self.assertEqual(response.status_code, 410)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Endpoint has been deprecated')
        self.assertEqual(data['detail'], 'Use PUT /notes/<note_id> instead')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/1/rename')

    def test_update_note_content(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            '/notes/1/content', data=json.dumps({'content': 'newcontent'}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 410)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Endpoint has been deprecated')
        self.assertEqual(data['detail'], 'Use PUT /notes/<note_id> instead')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/notes/1/content')

    def test_update_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': 'newname', 'content': 'newcontent'}),
            headers=self.headers_json,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['note']['name'], 'newname')
        self.assertEqual(data['note']['content'], 'newcontent')

    def test_update_empty(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        response = self.client.put(
            f'/notes/{note_id}', data=json.dumps({'name': None, 'content': None}), headers=self.headers_json
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse note update')
        self.assertEqual(data['detail'], "Missing mandatory field 'content'")

    def test_update_content(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': 'It now has a new name', 'content': self.note_full['content']}),
            headers=self.headers_json,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['name'], 'It now has a new name')
        self.assertEqual(data['note']['content'], self.note_full['content'])

    def test_update_name(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': self.note_full['name'], 'content': 'It now has new content'}),
            headers=self.headers_json,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['name'], self.note_full['name'])
        self.assertEqual(data['note']['content'], 'It now has new content')

    def test_update_note_blank_content(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        note_id = data['id']

        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps(self.note_blank_content),
            headers=self.headers_json,
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to parse note update')
        self.assertEqual(data['detail'], "'content' must not be blank")
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

    def test_get_my_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_full), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/notes', data=json.dumps(self.note_full2), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/notes/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note'][0]['owner'], str(self.user1.id))
        self.assertEqual(data['note'][0]['content'], self.note_full['content'])
        self.assertEqual(data['note'][0]['name'], self.note_full['name'])
        self.assertEqual(data['note'][1]['owner'], str(self.user1.id))
        self.assertEqual(data['note'][1]['content'], self.note_full2['content'])
        self.assertEqual(data['note'][1]['name'], self.note_full2['name'])
