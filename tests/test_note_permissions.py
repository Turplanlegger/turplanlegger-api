import json
import unittest
from uuid import uuid4

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class NotesPermissionTestCase(unittest.TestCase):
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
        cls.note_read_public = {
            'name': 'Notin pete read perms',
            'content': 'Wait a minute, these notes have permissions with them',
            'private': False,
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
        cls.note_modify_public = {
            'name': 'Notin pete modify perms',
            'content': 'Wait a minute, these notes have more permissions with them',
            'private': False,
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
        cls.note_delete_public = {
            'name': 'Notin pete modify perms',
            'content': 'Wait a minute, these notes have even more permissions with them',
            'private': False,
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

    def test_get_note_public(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read_public), headers=self.headers_json_user1)
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

        # User 3 - ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

    def test_update_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_modify), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note = json.loads(response.data.decode('utf-8'))
        note['content'] = 'Tripper'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_modify['name'], 'content': note.get('content')}),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('note'), note)

        # User 2 - ok
        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        note['content'] = 'Tripper2'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_modify['name'], 'content': note.get('content')}),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('note'), note)

        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        # User 3 - not ok
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'poopy'}),
            headers=self.headers_json_user3,
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note["id"]}')

    def test_update_note_public(self):
        response = self.client.post('/notes', data=json.dumps(self.note_modify_public), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note = json.loads(response.data.decode('utf-8'))
        note['content'] = 'Tripper'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({
                'name': self.note_modify['name'],
                'content': note.get('content'),
                'private': note.get('private')
            }),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('note'), note)

        # User 2 - ok
        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        note['content'] = 'Tripper2'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({
                'name': self.note_modify['name'],
                'content': note.get('content'),
                'private': note.get('private')
            }),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('note'), note)

        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)

        # User 3 - not ok
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'poopy'}),
            headers=self.headers_json_user3,
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 403)

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to modify the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note["id"]}')

    def test_update_note_fail(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note = json.loads(response.data.decode('utf-8'))
        note['content'] = 'Tripper'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({
                'name': note.get('name'),
                'content': note.get('content'),
                'private': note.get('private')
            }),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('note'), note)

        # User 2 - Not ok
        response = self.client.get(f'/notes/{note["id"]}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        note['content'] = 'Tripper2'
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_read['name'], 'content': note.get('content')}),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to modify the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note["id"]}')

        # User 3 - not ok
        response = self.client.put(
            f'/notes/{note["id"]}',
            data=json.dumps({'name': self.note_read['name'], 'content': 'poopy'}),
            headers=self.headers_json_user3,
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note["id"]}')

    def test_delete_note(self):
        response = self.client.post('/notes', data=json.dumps(self.note_delete), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user3)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

        # OK
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 404)

    def test_delete_note_public(self):
        response = self.client.post('/notes', data=json.dumps(self.note_delete_public), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user3)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to delete the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

        # OK
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 404)

    def test_delete_note_modify_fail(self):
        response = self.client.post('/notes', data=json.dumps(self.note_modify), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to delete the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

        # OK
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 200)

    def test_delete_note_read_fail(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to delete the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

        # OK
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 200)

    def test_change_note_owner(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change owner the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/owner')
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

        # Change owner
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 204)

        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 404)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['note']['permissions']), 1)
        self.assertEqual(data['note']['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['note']['permissions'][0]['object_id'], data['note']['id'])
        self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

    def test_change_note_owner_public(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read_public), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change owner the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/owner')
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 403)

        # Change owner
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 204)

        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['note']['permissions']), 1)
        self.assertEqual(data['note']['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['note']['permissions'][0]['object_id'], data['note']['id'])
        self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 403)

    def test_change_note_owner_modify(self):
        response = self.client.post('/notes', data=json.dumps(self.note_modify), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change owner the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/owner')
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

        # Change owner
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 204)

        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 404)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['note']['permissions']), 1)
        self.assertEqual(data['note']['permissions'][0]['access_level'], 'MODIFY')
        self.assertEqual(data['note']['permissions'][0]['object_id'], data['note']['id'])
        self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

    def test_change_note_owner_delete(self):
        response = self.client.post('/notes', data=json.dumps(self.note_delete), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 200)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user2
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change owner the note')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/owner')
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

        # Change owner
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user1
        )
        self.assertEqual(response.status_code, 204)

        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user1)
        self.assertEqual(response.status_code, 404)
        # Ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user2)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['note']['permissions']), 1)
        self.assertEqual(data['note']['permissions'][0]['access_level'], 'DELETE')
        self.assertEqual(data['note']['permissions'][0]['object_id'], data['note']['id'])
        self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))
        # Not ok
        response = self.client.get(f'/notes/{note_id}', headers=self.headers_user3)
        self.assertEqual(response.status_code, 404)
        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json_user3
        )
        self.assertEqual(response.status_code, 404)

    def test_add_permissions(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions',
            data=json.dumps(
                {
                    'permissions': [
                        {
                            'subject_id': str(self.user3.id),
                            'access_level': 'READ',
                        },
                    ]
                }
            ),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to add note permissions')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions')

        for user in (self.headers_json_user1, self.headers_json_user2):
            response = self.client.get(f'/notes/{note_id}', headers=user)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['note']['owner'], str(self.user1.id))
            self.assertEqual(data['note']['content'], self.note_read['content'])
            self.assertEqual(data['note']['name'], self.note_read['name'])
            self.assertEqual(len(data['note']['permissions']), 1)
            self.assertEqual(data['note']['permissions'][0]['access_level'], 'READ')
            self.assertEqual(data['note']['permissions'][0]['object_id'], note_id)
            self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))

        response = self.client.get(f'/notes/{note_id}', headers=self.headers_json_user3)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Note not found')
        self.assertEqual(data['detail'], 'The requested note was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}')

        # Ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions',
            data=json.dumps(
                {
                    'permissions': [
                        {
                            'subject_id': str(self.user3.id),
                            'access_level': 'READ',
                        },
                    ]
                }
            ),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['access_level'], 'READ')
        self.assertEqual(data['permissions'][0]['object_id'], note_id)
        self.assertEqual(data['permissions'][0]['subject_id'], str(self.user3.id))

        for user in (self.headers_json_user1, self.headers_json_user2, self.headers_json_user3):
            response = self.client.get(f'/notes/{note_id}', headers=user)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['note']['owner'], str(self.user1.id))
            self.assertEqual(data['note']['content'], self.note_read['content'])
            self.assertEqual(data['note']['name'], self.note_read['name'])
            self.assertEqual(len(data['note']['permissions']), 2)
            self.assertEqual(data['note']['permissions'][0]['access_level'], 'READ')
            self.assertEqual(data['note']['permissions'][0]['object_id'], note_id)
            self.assertEqual(data['note']['permissions'][0]['subject_id'], str(self.user2.id))
            self.assertEqual(data['note']['permissions'][1]['access_level'], 'READ')
            self.assertEqual(data['note']['permissions'][1]['object_id'], note_id)
            self.assertEqual(data['note']['permissions'][1]['subject_id'], str(self.user3.id))

    def test_add_existing_permissions(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions',
            data=json.dumps(
                {
                    'permissions': [
                        {
                            'subject_id': str(self.user2.id),
                            'access_level': 'READ',
                        },
                    ]
                }
            ),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Failed to add permissions')
        self.assertEqual(data['detail'], 'The permission already exists')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions')

    def test_delete_permissions(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.delete(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            headers=self.headers_json_user3,
        )
        self.assertEqual(response.status_code, 404)

        # Ok - Delete own permissions
        response = self.client.delete(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 204)
        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 404)

        # Re-create permission
        response = self.client.patch(
            f'/notes/{note_id}/permissions',
            data=json.dumps(
                {
                    'permissions': [
                        {
                            'subject_id': str(self.user2.id),
                            'access_level': 'READ',
                        },
                        {
                            'subject_id': str(self.user3.id),
                            'access_level': 'DELETE',
                        },
                    ]
                }
            ),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 200)

        # Not ok - Delete other users permissions
        response = self.client.delete(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            headers=self.headers_json_user3,
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to remove note permissions')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')

        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user3,
        )
        self.assertEqual(response.status_code, 200)

        # Ok - Delete users permissions
        response = self.client.delete(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 204)
        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 404)

        # Not ok - Delete non existing permissions
        response = self.client.delete(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to delete permissions')
        self.assertEqual(data['detail'], 'User not found in permissions')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')
        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_permissions(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODIFY'}),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change permissions')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')
        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'tripper'}),
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 403)

        # Ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODIFY'}),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['permission']['access_level'], 'MODIFY')
        self.assertEqual(data['permission']['object_id'], note_id)
        self.assertEqual(data['permission']['subject_id'], str(self.user2.id))

        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'tripper'}),
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 200)

        # Not ok - non-existing access level
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODEFY'}),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to update permissions')
        self.assertEqual(data['detail'], 'Ensure access level is one of READ, MODIFY, OR DELETE')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')

        # Ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'DELETE'}),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['permission']['access_level'], 'DELETE')
        self.assertEqual(data['permission']['object_id'], note_id)
        self.assertEqual(data['permission']['subject_id'], str(self.user2.id))

        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 404)

    def test_update_permissions_public(self):
        response = self.client.post('/notes', data=json.dumps(self.note_read_public), headers=self.headers_json_user1)
        self.assertEqual(response.status_code, 201)
        note_id = json.loads(response.data.decode('utf-8'))['id']

        # Not ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODIFY'}),
            headers=self.headers_json_user2,
        )

        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Insufficient permissions')
        self.assertEqual(data['detail'], 'Not sufficient permissions to change permissions')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')
        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'tripper'}),
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 403)

        # Ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODIFY'}),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['permission']['access_level'], 'MODIFY')
        self.assertEqual(data['permission']['object_id'], note_id)
        self.assertEqual(data['permission']['subject_id'], str(self.user2.id))

        response = self.client.get(
            f'/notes/{note_id}',
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.put(
            f'/notes/{note_id}',
            data=json.dumps({'name': self.note_modify['name'], 'content': 'tripper'}),
            headers=self.headers_json_user2,
        )
        self.assertEqual(response.status_code, 200)

        # Not ok - non-existing access level
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'MODEFY'}),
            headers=self.headers_json_user1,
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Failed to update permissions')
        self.assertEqual(data['detail'], 'Ensure access level is one of READ, MODIFY, OR DELETE')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/notes/{note_id}/permissions/{str(self.user2.id)}')

        # Ok
        response = self.client.patch(
            f'/notes/{note_id}/permissions/{str(self.user2.id)}',
            data=json.dumps({'access_level': 'DELETE'}),
            headers=self.headers_json_user1,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['permission']['access_level'], 'DELETE')
        self.assertEqual(data['permission']['object_id'], note_id)
        self.assertEqual(data['permission']['subject_id'], str(self.user2.id))

        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(f'/notes/{note_id}', headers=self.headers_json_user2)
        self.assertEqual(response.status_code, 404)
