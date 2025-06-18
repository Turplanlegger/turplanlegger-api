import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class ItemListsPermissionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'DEDBUG',
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
        cls.user3 = User.create(
            User(
                name='Bård',
                last_name='Nordamnn',
                email='baard.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test'),
            )
        )

        cls.item_list_read = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': True,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.item_list_modify = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': True,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.item_list_delete = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': True,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'DELETE',
                },
            ],
        }
        cls.item_list_public_read = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': False,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'READ',
                },
            ],
        }
        cls.item_list_public_modify = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': False,
            'permissions': [
                {
                    'subject_id': str(cls.user2.id),
                    'access_level': 'MODIFY',
                },
            ],
        }
        cls.item_list_public_delete = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
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
        db.truncate_table('lists_items')
        db.truncate_table('item_lists')
        db.truncate_table('item_list_permissions')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_add_list_ok(self):
        for item_list in (
            self.item_list_read,
            self.item_list_modify,
            self.item_list_delete,
            self.item_list_public_read,
            self.item_list_public_modify,
            self.item_list_public_delete
        ):
            response = self.client.post('/item_lists', data=json.dumps(item_list), headers=self.headers_json_user1)
            self.assertEqual(response.status_code, 201)

            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['item_list']['owner'], str(self.user1.id))

            self.assertEqual(data['item_list']['private'], item_list.get('private'))
            self.assertEqual(data['item_list']['owner'], str(self.user1.id))
            self.assertEqual(len(data['item_list']['permissions']), 1)
            self.assertEqual(data['item_list']['permissions'][0]['access_level'], item_list.get('permissions')[0].get('access_level'))
            self.assertEqual(data['item_list']['permissions'][0]['object_id'], data['id'])
            self.assertEqual(data['item_list']['permissions'][0]['subject_id'], str(self.user2.id))
