import json
import unittest
from uuid import uuid4

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class ItemListsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test',
            'SECRET_KEY_ID': 'test',
            'LOG_LEVEL': 'INFO',
            'CREATE_ADMIN_USER': True
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
                password=hash_password('test')
            )
        )
        cls.user2 = User.create(
            User(
                id=str(uuid4()),
                name='Kari',
                last_name='Nordamnn',
                email='kari.nordmann@norge.no',
                auth_method='basic',
                password=hash_password('test')
            )
        )

        cls.item_list = {
            'name': 'Test list',
            'items': [
                'item one',
                'item two',
                'item three'
            ],
            'items_checked': [
                'item four',
                'item five'
            ],
            'owner': cls.user1.id,
            'type': 'check'
        }

        cls.empty_item_list = {
            'name': 'Empty test list',
            'items': [],
            'items_checked': [],
            'owner': cls.user1.id,
            'type': 'check'
        }

        cls.item_to_add = {
            'items': [
                'item one',
                'item two',
            ],
            'items_checked': [
                'item three'
            ]
        }

        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user1.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'}
        )
        if response.status_code != 200:
            raise RuntimeError('Failed to login')

        data = json.loads(response.data.decode('utf-8'))

        cls.headers_json = {
            'Content-type': 'application/json',
            'Authorization': f'Bearer {data["token"]}'
        }
        cls.headers = {
            'Authorization': f'Bearer {data["token"]}'
        }

    def tearDown(self):
        db.truncate_table('lists_items')
        db.truncate_table('item_lists')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_create_list(self):
        response = self.client.post(
            '/item_list',
            data=json.dumps(self.item_list),
            headers=self.headers_json
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], self.user1.id)
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(data['item_list']['items'][0]['content'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['content'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][2]['content'], 'item three')
        self.assertEqual(data['item_list']['items'][2]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][2]['item_list'], data['item_list']['id'])
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 2)
        self.assertEqual(data['item_list']['items_checked'][0]['content'], 'item four')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][1]['content'], 'item five')
        self.assertEqual(data['item_list']['items_checked'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][1]['item_list'], data['item_list']['id'])

    def test_create_empty_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], self.user1.id)
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 0)
        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], self.user1.id)
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 0)

    def test_get_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.get(
            f'/item_list/{list_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], self.user1.id)
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(data['item_list']['items'][0]['content'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['content'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][2]['content'], 'item three')
        self.assertEqual(data['item_list']['items'][2]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][2]['item_list'], data['item_list']['id'])
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 2)
        self.assertEqual(data['item_list']['items_checked'][0]['content'], 'item four')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][1]['content'], 'item five')
        self.assertEqual(data['item_list']['items_checked'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][1]['item_list'], data['item_list']['id'])

    def test_list_not_found(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            '/item_list/2',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Item list not found')
        self.assertEqual(data['detail'], 'The requested item list was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/item_list/2')

    def test_delete_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.delete(
            f'/item_list/{list_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

    def test_add_to_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        created_data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f"/item_list/{created_data['id']}/add",
                                     data=json.dumps(self.item_to_add), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)
        added_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(added_data['status'], 'ok')
        self.assertEqual(added_data['count_items'], 2)
        self.assertEqual(added_data['count_items_checked'], 1)

        response = self.client.get(
            f"/item_list/{created_data['id']}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], created_data['item_list']['name'])
        self.assertEqual(data['item_list']['owner'], created_data['item_list']['owner'])
        self.assertEqual(data['item_list']['type'], created_data['item_list']['type'])
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 2)
        self.assertEqual(data['item_list']['items'][0]['content'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['content'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 1)
        self.assertEqual(data['item_list']['items_checked'][0]['content'], 'item three')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])

    def test_rename_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(
            f'/item_list/{list_id}/rename',
            data=json.dumps({'name': 'new list name'}),
            headers=self.headers_json
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/item_list/{list_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['name'], 'new list name')

    def test_change_list_owner(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(
            f'/item_list/{list_id}/owner',
            data=json.dumps({'owner': self.user2.id}),
            headers=self.headers_json
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/item_list/{list_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['owner'], self.user2.id)

    def test_toggle_check(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        toggle_list_items = [
            create_data['item_list']['items'][0]['id'],
            create_data['item_list']['items_checked'][0]['id']
        ]

        response = self.client.patch(f'/item_list/{list_id}/toggle_check',
                                     data=json.dumps({'items': toggle_list_items}), headers=self.headers_json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/item_list/{list_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(len(data['item_list']['items_checked']), 2)
