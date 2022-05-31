import json
import unittest

from turplanlegger.app import create_app, db


class ItemListsTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True,
            'LOG_LEVEL': 'INFO'
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        # Users isn't implemented yet, so they have to be created manually for the time being
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

        self.item_list = {
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
            'owner': 1,
            'type': 'check'
        }

        self.empty_item_list = {
            'name': 'Empty test list',
            'items': [],
            'items_checked': [],
            'owner': 1,
            'type': 'check'
        }

        self.item_to_add = {
            'items': [
                'item one',
                'item two',
            ],
            'items_checked': [
                'item three'
            ]
        }

        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):
        db.destroy()

    def test_create_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
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
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(len(data['item_list']['items']), 0)
        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertEqual(len(data['item_list']['items_checked']), 0)

    def test_get_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.get(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
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
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        response = self.client.get('/item_list/2')
        self.assertEqual(response.status_code, 404)

    def test_delete_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.delete(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)

    def test_add_to_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        created_data = json.loads(response.data.decode('utf-8'))

        response = self.client.patch(f"/item_list/{created_data['id']}/add",
                                     data=json.dumps(self.item_to_add), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        added_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(added_data['status'], 'ok')
        self.assertEqual(added_data['count_items'], 2)
        self.assertEqual(added_data['count_items_checked'], 1)

        response = self.client.get(f"/item_list/{created_data['id']}")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], created_data['item_list']['name'])
        self.assertEqual(data['item_list']['owner'], created_data['item_list']['owner'])  # Update to user created
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
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(f'/item_list/{list_id}/rename',
                                     data=json.dumps({'name': 'new list name'}), headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['name'], 'new list name')

    def test_change_list_owner(self):
        response = self.client.post('/item_list', data=json.dumps(self.empty_item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        response = self.client.patch(f'/item_list/{list_id}/owner', data=json.dumps({'owner': 2}), headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['owner'], 2)

    def test_toggle_check(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        create_data = json.loads(response.data.decode('utf-8'))
        list_id = create_data['id']

        toggle_list_items = [
            create_data['item_list']['items'][0]['id'],
            create_data['item_list']['items_checked'][0]['id']
        ]

        response = self.client.patch(f'/item_list/{list_id}/toggle_check',
                                     data=json.dumps({'items': toggle_list_items}), headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(data['item_list']['items']), 3)
        self.assertEqual(len(data['item_list']['items_checked']), 2)
