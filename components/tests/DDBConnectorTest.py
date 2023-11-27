import aiounittest
import unittest
import asyncio
import aioboto3
from components.database.DDBConnector import DDBConnector
from boto3.dynamodb.conditions import Key
from decimal import Decimal

class TestDDBConnectorIntegration(aiounittest.AsyncTestCase):

    def setUp(self):
        self.chats_table = "chats_test"
        self.users_table = "authorized_users"
        self.connector = DDBConnector(chats_table=self.chats_table, users_table=self.users_table)

        self.sample_user_data = {'email': 'test@example.com'}
        self.sample_user_data2 = {'email': 'test2@example.com'}
        self.sample_chat_data = {
                                    "chat_id": 1,
                                    "user_email": "test@example.com",
                                    "timestamp": 1234567789,
                                    "messages": [
                                        {
                                        "type": "user",
                                        "content": "some content"
                                        },
                                        {
                                        "type": "peer",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }

        self.sample_chat_data2 = {
                                    "chat_id": 2,
                                    "user_email": "test@example.com",
                                    "timestamp": 1234567789,
                                    "messages": [
                                        {
                                        "type": "user",
                                        "content": "some content"
                                        },
                                        {
                                        "type": "peer",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }


        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._insert_sample_data(self.users_table, self.sample_user_data))
        loop.run_until_complete(self._insert_sample_data(self.chats_table, self.sample_chat_data))
        loop.run_until_complete(self._insert_sample_data(self.users_table, self.sample_user_data2))
        loop.run_until_complete(self._insert_sample_data(self.chats_table, self.sample_chat_data2))

    async def _insert_sample_data(self, table_name, data):
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(table_name)
            await table.put_item(Item=data)

    async def _delete_sample_data(self, table_name, key):
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(table_name)
            await table.delete_item(Key=key)

    def tearDown(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._delete_sample_data(self.users_table, {'email': 'test@example.com'}))
        loop.run_until_complete(self._delete_sample_data(self.chats_table, {'chat_id': 1, 'timestamp': 1234567789}))
        loop.run_until_complete(self._delete_sample_data(self.users_table, {'email': 'test2@example.com'}))
        loop.run_until_complete(self._delete_sample_data(self.chats_table, {'chat_id': 2, 'timestamp': 1234567789}))


    async def test_integration_get_chats_by_email(self):
        # Given a test email
        email = "test@example.com"
        result = await self.connector.get_chats_by_email(email)
        expected = [{'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': Decimal('2'), 'timestamp': Decimal('1234567789')}, {'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': Decimal('1'), 'timestamp': Decimal('1234567789')}]
        self.assertEqual(result, expected)

    async def test_get_chat_by_id(self):
        pass

    async def test_delete_chat_by_id(self):
        pass

    async def test_get_user(self):
        pass

    async def test_store_chat(self):
        pass
        

if __name__ == '__main__':
    unittest.main()
