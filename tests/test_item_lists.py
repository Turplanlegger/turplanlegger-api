import json
import unittest

from turplanlegger.app import create_app  # ,  db

class ItemListsTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        # Users isn't implemented yet, so they have to be created manually for the time being
        self.user1 = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no'
        }
        self.user1 = {
            'name': 'Kari',
            'last_name': 'Nordamnn',
            'email': 'kari.nordmann@norge.no'
        }

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

    # def tearDown(self):
        # db.destroy()

    def test_create_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertCountEqual(data['item_list']['items'], 3)
        self.assertEqual(data['item_list']['items'][0]['name'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['name'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][2]['name'], 'item three')
        self.assertEqual(data['item_list']['items'][2]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][2]['item_list'], data['item_list']['id'])
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertCountEqual(data['item_list']['items_checked'], 2)
        self.assertEqual(data['item_list']['items_checked'][0]['name'], 'item four')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][1]['name'], 'item five')
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
        self.assertDictEqual(data['item_list']['items'], [])
        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertDictEqual(data['item_list']['items_checked'], [])

    def test_get_list(self):
        response = self.client.post('/item_list', data=json.dumps(self.item_list), headers=self.headers)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        list_id = data['id']

        response = self.client.get(f'/item_list/{list_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], 1)  # Update to user created
        self.assertEqual(data['item_list']['type'], 'check')
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertCountEqual(data['item_list']['items'], 3)
        self.assertEqual(data['item_list']['items'][0]['name'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][1]['name'], 'item two')
        self.assertEqual(data['item_list']['items'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][1]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items'][2]['name'], 'item three')
        self.assertEqual(data['item_list']['items'][2]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items'][2]['item_list'], data['item_list']['id'])
        self.assertIsInstance(data['item_list']['items_checked'], list)
        self.assertCountEqual(data['item_list']['items_checked'], 2)
        self.assertEqual(data['item_list']['items_checked'][0]['name'], 'item four')
        self.assertEqual(data['item_list']['items_checked'][0]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][0]['item_list'], data['item_list']['id'])
        self.assertEqual(data['item_list']['items_checked'][1]['name'], 'item five')
        self.assertEqual(data['item_list']['items_checked'][1]['owner'], data['item_list']['owner'])
        self.assertEqual(data['item_list']['items_checked'][1]['item_list'], data['item_list']['id'])


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

        self.assertEqual(added_data['count'], 1)
        self.assertEqual(added_data['item_list']['name'], created_data['item_list']['name'])
        self.assertEqual(added_data['item_list']['owner'], created_data['item_list']['owner'])  # Update to user created
        self.assertEqual(added_data['item_list']['type'], created_data['item_list']['type'])
        self.assertIsInstance(added_data['item_list']['items'], list)
        self.assertCountEqual(added_data['item_list']['items'], 2)
        self.assertEqual(added_data['item_list']['items'][0]['name'], 'item one')
        self.assertEqual(added_data['item_list']['items'][0]['owner'], added_data['item_list']['owner'])
        self.assertEqual(added_data['item_list']['items'][0]['item_list'], added_data['item_list']['id'])
        self.assertEqual(added_data['item_list']['items'][1]['name'], 'item two')
        self.assertEqual(added_data['item_list']['items'][1]['owner'], added_data['item_list']['owner'])
        self.assertEqual(added_data['item_list']['items'][1]['item_list'], added_data['item_list']['id'])
        self.assertIsInstance(added_data['item_list']['items_checked'], list)
        self.assertCountEqual(added_data['item_list']['items_checked'], 1)
        self.assertEqual(added_data['item_list']['items_checked'][0]['name'], 'item three')
        self.assertEqual(added_data['item_list']['items_checked'][0]['owner'], added_data['item_list']['owner'])
        self.assertEqual(added_data['item_list']['items_checked'][0]['item_list'], added_data['item_list']['id'])
