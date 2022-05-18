import json
import unittest

from turplanlegger.app import create_app, db

class ItemListsTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'TESTING': True
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

        # Users isn't implemented yet, so they have to be created manually for the time being
        self.user = {
            'name': 'Ola',
            'last_name': 'Nordamnn',
            'email': 'ola.nordmann@norge.no'
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
                'item why would you add a checked one?!'
            ],
            'owner': 1,
            'type': 'check'
        }''

        self.empty_item_list = {
            'name': 'Empty test list',
            'items': [],
            'items_checked': [],
            'owner': 1,
            'type': 'check'
        }

        self.headers = {
            'Content-type': 'application/json'
        }


    def tearDown(self):
        db.destroy()

    def test_create_list(self):
        response = self.client.post('item_list', data=json.dumps(self.item_list), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['item_list']['name'], 'Empty test list')
        self.assertEqual(data['item_list']['owner'], 1) # Update to user created
        self.assertIsInstance(data['item_list']['items'], list)
        self.assertEqual(data['item_list']['items'][0]['name'], 'item one')
        self.assertEqual(data['item_list']['items'][0]['owner'], 1)
        self.assertEqual(data['item_list']['items'][0]['item_list'], data['item_list']['id'])
