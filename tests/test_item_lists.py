import json
import unittest

from turplanlegger.app import create_app, db
from turplanlegger.auth.utils import hash_password
from turplanlegger.models.user import User


class ItemListsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
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

        cls.item_list = {
            'name': 'Test list',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': True,
        }

        cls.item_list2 = {
            'name': 'Test list 2',
            'items': [
                {'content': 'This list has less items'},
            ],
            'items_checked': [
                {'content': 'only one checked'},
            ],
        }

        cls.item_list_public = {
            'name': 'Test list public',
            'items': [{'content': 'item one'}, {'content': 'item two'}, {'content': 'item three'}],
            'items_checked': [{'content': 'item four'}, {'content': 'item five'}],
            'private': False,
        }

        cls.empty_item_list = {'name': 'Empty test list', 'items': [], 'items_checked': [], 'private': True}

        cls.item_to_add = {
            'items': [
                {'content': 'item one'},
                {'content': 'item two'},
            ],
            'items_checked': [{'content': 'item three'}],
        }

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

        response = cls.client.post(
            '/login',
            data=json.dumps({'email': cls.user2.email, 'password': 'test'}),
            headers={'Content-type': 'application/json'},
        )
        if response.status_code != 200:
            raise RuntimeError('Failed to login')
        data = json.loads(response.data.decode('utf-8'))
        cls.user2_headers_json = {'Content-type': 'application/json', 'Authorization': f'Bearer {data["token"]}'}
        cls.user2_headers = {'Authorization': f'Bearer {data["token"]}'}

    def tearDown(self):
        db.truncate_table('lists_items')
        db.truncate_table('item_lists')

    @classmethod
    def tearDownClass(cls):
        db.destroy()

    def test_create_list_minimal_input(self):
        response = self.client.post('/item_lists', data=json.dumps({}), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['private'], True)
        self.assertEqual(data['item_list']['owner'], str(self.user1.id))

    def test_create_list(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], str(self.user1.id))
        self.assertEqual(data['item_list']['private'], self.item_list['private'])
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
        response = self.client.post('/item_lists', data=json.dumps(self.empty_item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], str(self.user1.id))
        self.assertEqual(data['item_list']['private'], self.empty_item_list['private'])
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 0)

    def test_get_list(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.get(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], str(self.user1.id))
        self.assertEqual(data['item_list']['private'], self.item_list['private'])
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(data['item_list']['items'][0]['content'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][0]['checked'], False)
        self.assertEqual(data['item_list']['items'][1]['content'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['checked'], False)
        self.assertEqual(data['item_list']['items'][2]['content'], 'item three')
        self.assertEqual(data['item_list']['items'][2]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][2]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][2]['checked'], False)
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 2)
        self.assertEqual(data['item_list']['items_checked'][0]['content'], 'item four')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][0]['checked'], True)
        self.assertEqual(data['item_list']['items_checked'][1]['content'], 'item five')
        self.assertEqual(data['item_list']['items_checked'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][1]['checked'], True)

    def test_list_not_found(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)

        response = self.client.get('/item_lists/2', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Item list not found')
        self.assertEqual(data['detail'], 'The requested item list was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], 'http://localhost/item_lists/2')

    def test_delete_list(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.delete(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Item list not found')
        self.assertEqual(data['detail'], 'The requested item list was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/item_lists/{list_id}')

    def test_add_to_list(self):
        response = self.client.post('/item_lists', data=json.dumps(self.empty_item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)
        created_data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(
            f'/item_lists/{created_data["id"]}/add', data=json.dumps(self.item_to_add), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 200)
        added_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(added_data['status'], 'ok')
        self.assertEqual(added_data['count_items'], 2)
        self.assertEqual(added_data['count_items_checked'], 1)

        response = self.client.get(f'/item_lists/{created_data["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], created_data['item_list']['name'])
        self.assertEqual(data['item_list']['owner'], created_data['item_list']['owner'])
        self.assertEqual(data['item_list']['private'], created_data['item_list']['private'])
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
        response = self.client.post('/item_lists', data=json.dumps(self.empty_item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(
            f'/item_lists/{list_id}/rename', data=json.dumps({'name': 'new list name'}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['name'], 'new list name')

    def test_change_list_owner(self):
        response = self.client.post('/item_lists', data=json.dumps(self.empty_item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(
            f'/item_lists/{list_id}/owner', data=json.dumps({'owner': str(self.user2.id)}), headers=self.headers_json
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Item list not found')
        self.assertEqual(data['detail'], 'The requested item list was not found')
        self.assertEqual(data['type'], 'about:blank')
        self.assertEqual(data['instance'], f'http://localhost/item_lists/{list_id}')

    def test_toggle_check(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        toggle_list_items = [
            create_data['item_list']['items'][0]['id'],
            create_data['item_list']['items_checked'][0]['id'],
        ]

        response = self.client.patch(
            f'/item_lists/{list_id}/toggle_check',
            data=json.dumps({'toggle_items': toggle_list_items}),
            headers=self.headers_json,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_lists/{list_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(data['item_list']['items'][0]['content'], self.item_list['items'][1]['content'])
        self.assertEqual(data['item_list']['items'][1]['content'], self.item_list['items'][2]['content'])
        self.assertEqual(data['item_list']['items'][2]['content'], self.item_list['items_checked'][0]['content'])
        self.assertEqual(len(data['item_list']['items_checked']), 2)
        self.assertEqual(
            data['item_list']['items_checked'][0]['content'], self.item_list['items_checked'][1]['content']
        )
        self.assertEqual(data['item_list']['items_checked'][1]['content'], self.item_list['items'][0]['content'])

    def test_get_my_list(self):
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/item_lists', data=json.dumps(self.item_list2), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/item_lists/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['count'], 2)
        self.assertEqual(data['item_list'][0]['id'], 1)
        self.assertEqual(data['item_list'][0]['name'], self.item_list['name'])
        self.assertEqual(data['item_list'][0]['owner'], str(self.user1.id))
        self.assertEqual(data['item_list'][0]['private'], self.item_list['private'])
        self.assertEqual(data['item_list'][0]['items'][0]['content'], self.item_list['items'][0]['content'])
        self.assertEqual(data['item_list'][0]['items'][0]['owner'], data['item_list'][0]['owner'])
        self.assertEqual(data['item_list'][0]['items'][0]['item_list'], data['item_list'][0]['id'])
        self.assertEqual(data['item_list'][0]['items'][1]['content'], self.item_list['items'][1]['content'])
        self.assertEqual(data['item_list'][0]['items'][1]['owner'], data['item_list'][0]['owner'])
        self.assertEqual(data['item_list'][0]['items'][1]['item_list'], data['item_list'][0]['id'])
        self.assertEqual(data['item_list'][0]['items'][2]['content'], self.item_list['items'][2]['content'])
        self.assertEqual(data['item_list'][0]['items'][2]['owner'], data['item_list'][0]['owner'])
        self.assertEqual(data['item_list'][0]['items'][2]['item_list'], data['item_list'][0]['id'])
        self.assertEqual(
            data['item_list'][0]['items_checked'][0]['content'], self.item_list['items_checked'][0]['content']
        )
        self.assertEqual(data['item_list'][0]['items_checked'][0]['owner'], data['item_list'][0]['owner'])
        self.assertEqual(data['item_list'][0]['items_checked'][0]['item_list'], data['item_list'][0]['id'])
        self.assertEqual(
            data['item_list'][0]['items_checked'][1]['content'], self.item_list['items_checked'][1]['content']
        )
        self.assertEqual(data['item_list'][0]['items_checked'][1]['owner'], data['item_list'][0]['owner'])
        self.assertEqual(data['item_list'][0]['items_checked'][1]['item_list'], data['item_list'][0]['id'])

        self.assertEqual(data['item_list'][1]['id'], 2)
        self.assertEqual(data['item_list'][1]['name'], self.item_list2['name'])
        self.assertEqual(data['item_list'][1]['owner'], str(self.user1.id))
        self.assertEqual(data['item_list'][1]['private'], True)
        self.assertEqual(data['item_list'][1]['items'][0]['content'], self.item_list2['items'][0]['content'])
        self.assertEqual(data['item_list'][1]['items'][0]['owner'], data['item_list'][1]['owner'])
        self.assertEqual(data['item_list'][1]['items'][0]['item_list'], data['item_list'][1]['id'])
        self.assertEqual(
            data['item_list'][1]['items_checked'][0]['content'], self.item_list2['items_checked'][0]['content']
        )
        self.assertEqual(data['item_list'][1]['items_checked'][0]['owner'], data['item_list'][1]['owner'])
        self.assertEqual(data['item_list'][1]['items_checked'][0]['item_list'], data['item_list'][1]['id'])

    def test_get_all_public_list(self):
        # User1
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/item_lists', data=json.dumps(self.item_list2), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/item_lists', data=json.dumps(self.item_list_public), headers=self.headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/item_lists/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get('/item_lists/mine', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['count'], 3)

        # User2
        response = self.client.post('/item_lists', data=json.dumps(self.item_list), headers=self.user2_headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/item_lists', data=json.dumps(self.item_list2), headers=self.user2_headers_json)
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            '/item_lists', data=json.dumps(self.item_list_public), headers=self.user2_headers_json
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/item_lists/mine', headers=self.user2_headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        response = self.client.get('/item_lists/mine', headers=self.user2_headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['count'], 3)

        response = self.client.get('/item_lists/public', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['count'], 2)

        response = self.client.get('/item_lists/public', headers=self.user2_headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['count'], 2)
