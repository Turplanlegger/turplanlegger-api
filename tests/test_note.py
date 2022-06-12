import json
import unittest

from turplanlegger.app import create_app, db


class NotesTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        self.user1 = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no'
        }
        self.user2 = {
            'name': 'Kari',
            'last_name': 'Nordamnn',
            'email': 'kari.nordmann@norge.no'
        }

        db.create_user(self.user1['name'], self.user1['last_name'], self.user1['email'])
        db.create_user(self.user2['name'], self.user2['last_name'], self.user2['email'])

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
        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):
        db.destroy()

    def test_add_note_ok(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['owner'], 1)

    def test_add_note_no_owner(self):
        response = self.client.post('/note', data=json.dumps(self.note_no_owner), headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Missing mandatory field "owner"')

    def test_get_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_note_id = data['id']

        response = self.client.get(f'/note/{created_note_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], self.note_full['owner'])

    def test_get_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/note/2')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'note not found')

    def test_delete_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_note_id = data['id']

        response = self.client.delete(f'/note/{created_note_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('/note/2')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'note not found')

    def test_change_note_owner(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        created_note_id = data['id']

        response = self.client.patch(f'/note/{created_note_id}/owner',
                                     data=json.dumps({'owner': 2}), headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/note/{created_note_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['note']['owner'], 2)

    def test_change_note_owner_note_not_found(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/2/owner', data=json.dumps({'owner': 2}), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'note not found')

    def test_change_note_owner_no_owner_given(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/1/owner', data=json.dumps({}), headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'must supply owner as int')

    def test_rename_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/1/rename', data=json.dumps({'name': 'newlist'}), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')

    def test_update_note(self):
        response = self.client.post('/note', data=json.dumps(self.note_full), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch('/note/1/update', data=json.dumps({'content': 'newcontent'}), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')
