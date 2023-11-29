import aiounittest
import asyncio
import aioboto3
from components.database.DDBConnector import DDBConnector
from decimal import Decimal

class TestDDBConnectorIntegration(aiounittest.AsyncTestCase):

    def setUp(self):
        self.chats_table = "chats_test"
        self.users_table = "authorized_users"
        self.connector = DDBConnector.getInstance(chats_table=self.chats_table, users_table=self.users_table)

        self.sample_user_data = {'email': 'test@example.com'}
        self.sample_user_data2 = {'email': 'test2@example.com'}
        self.sample_chat_data = {
                                    "chat_id": 'randomUUID1',
                                    "user_email": "test@example.com",
                                    "timestamp": 1234567789,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": "base64"
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }

        self.sample_chat_data2 = {
                                    "chat_id": 'randomUUID2',
                                    "user_email": "test@example.com",
                                    "timestamp": 1234567789,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": ""
                                        },
                                        {
                                        "role": "assistant",
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
        loop.run_until_complete(self._delete_sample_data(self.chats_table, {'chat_id': 'randomUUID1'}))
        loop.run_until_complete(self._delete_sample_data(self.users_table, {'email': 'test2@example.com'}))
        loop.run_until_complete(self._delete_sample_data(self.chats_table, {'chat_id': 'randomUUID2'}))


    async def test_integration_get_chats_by_email(self):
        # Given a test email
        email = "test@example.com"
        result = await self.connector.get_chats_by_email(email)
        expected = [{'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID1', 'timestamp': Decimal('1234567789')}, {'messages': [{'role': 'user', 'content': 'some content', 'image': ''}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID2', 'timestamp': Decimal('1234567789')}]
        self.assertEqual(result, expected)

        # Given email without chats
        email = "test2@example.com"
        result = await self.connector.get_chats_by_email(email)
        expected = []
        self.assertEqual(result, expected)

    async def test_get_chat_by_id(self):
        id = 'randomUUID1'
        result = await self.connector.get_chat_by_id(id)
        expected = {'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID1', 'timestamp': Decimal('1234567789')}
        self.assertDictEqual(result, expected)

    async def test_update_item(self):
        id = 'randomUUID11'
        sample_chat_data = {
                                    "chat_id": id,
                                    "user_email": "test3@example.com",
                                    "timestamp": 1234349495,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": "base64"
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }
        await self.connector.store_chat(sample_chat_data)
        sample_chat_data_updated = {
                                    "chat_id": id,
                                    "user_email": "test3@example.com",
                                    "timestamp": 4534534324,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": "base64"
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer"
                                        },
                                        {
                                        "role": "user",
                                        "content": "some content 2",
                                        "image": ""
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer answer"
                                        }
                                    ]
                                }
        await self.connector.store_chat(sample_chat_data_updated)
        result = await self.connector.get_chat_by_id(id)
        expected = { "chat_id": "randomUUID11", "user_email": "test3@example.com", "timestamp": Decimal('4534534324'), "messages": [ { "role": "user", "content": "some content", "image": "base64" }, { "role": "assistant", "content": "some content from peer" }, { "role": "user", "content": "some content 2", "image": "" }, { "role": "assistant", "content": "some content from peer answer" } ] }
        self.assertDictEqual(result, expected)
        await self.connector.delete_chat_by_id(id)

    async def test_delete_chat_by_id(self):
        id = 'randomUUID10'
        ts = 1234349495
        sample_chat_data = {
                                    "chat_id": id,
                                    "user_email": "test@example.com",
                                    "timestamp": ts,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": "base64"
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }
        await self._insert_sample_data(self.chats_table, sample_chat_data)
        await self.connector.delete_chat_by_id(id)
        result = await self.connector.get_chat_by_id(id)
        self.assertIsNone(result)

    async def test_get_user(self):
        email = "test2@example.com"
        result = await self.connector.get_user(email)
        expected = {'email': 'test2@example.com'}
        self.assertDictEqual(result, expected)

    async def test_store_chat(self):
        id = 'randomUUID15'
        ts = 1234567789
        sample_chat_data = {
                                    "chat_id": id,
                                    "user_email": "test@example.com",
                                    "timestamp": ts,
                                    "messages": [
                                        {
                                        "role": "user",
                                        "content": "some content",
                                        "image": "base64"
                                        },
                                        {
                                        "role": "assistant",
                                        "content": "some content from peer"
                                        }
                                    ]
                                }
        await self.connector.store_chat(sample_chat_data)
        result = await self.connector.get_chat_by_id(id)
        expected = {'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID15', 'timestamp': Decimal('1234567789')}
        self.assertDictEqual(result, expected)
        await self.connector.delete_chat_by_id(id)
