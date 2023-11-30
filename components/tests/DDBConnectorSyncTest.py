import boto3
import aiounittest
from components.database.DDBConnectorSync import DDBConnectorSync
from decimal import Decimal

class TestDDBConnectorIntegration(aiounittest.AsyncTestCase):

    def setUp(self):
        self.chats_table = "chats_test"
        self.users_table = "authorized_users"
        self.connector = DDBConnectorSync(chats_table=self.chats_table, users_table=self.users_table)

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


        self._insert_sample_data(self.users_table, self.sample_user_data)
        self._insert_sample_data(self.chats_table, self.sample_chat_data)
        self._insert_sample_data(self.users_table, self.sample_user_data2)
        self._insert_sample_data(self.chats_table, self.sample_chat_data2)

    def _insert_sample_data(self, table_name, data):
        resource = boto3.resource("dynamodb")
        table = resource.Table(table_name)
        table.put_item(Item=data)

    def _delete_sample_data(self, table_name, key):
        resource = boto3.resource("dynamodb")
        table = resource.Table(table_name)
        table.delete_item(Key=key)

    def tearDown(self):
        self._delete_sample_data(self.users_table, {'email': 'test@example.com'})
        self._delete_sample_data(self.chats_table, {'chat_id': 'randomUUID1', 'timestamp': 1234567789})
        self._delete_sample_data(self.users_table, {'email': 'test2@example.com'})
        self._delete_sample_data(self.chats_table, {'chat_id': 'randomUUID2','timestamp': 1234567789})


    async def test_integration_get_chats_by_email(self):
        # Given a test email
        email = "test@example.com"
        result = await self.connector.get_chats_by_email(email)
        expected = [{'messages': [{'role': 'user', 'content': 'some content', 'image': ''}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID2', 'timestamp': Decimal('1234567789')}, {'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID1', 'timestamp': Decimal('1234567789')}]
        self.assertEqual(result, expected)

        # Given email without chats
        email = "test2@example.com"
        result =  await self.connector.get_chats_by_email(email)
        expected = []
        self.assertEqual(result, expected)

    async def test_get_chat_by_id(self):
        id = 'randomUUID1'
        ts = 1234567789
        result =  await self.connector.get_chat_by_id(id, ts)
        expected = {'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID1', 'timestamp': Decimal('1234567789')}
        self.assertDictEqual(result, expected)

    async def test_update_item(self):
        id = 'randomUUID11'
        ts = 1234349495
        sample_chat_data = {
                                    "chat_id": id,
                                    "user_email": "test3@example.com",
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
        sample_chat_data_updated = {
                                    "chat_id": id,
                                    "user_email": "test3@example.com",
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
        result =  await self.connector.get_chat_by_id(id, ts)
        expected = { "chat_id": "randomUUID11", "user_email": "test3@example.com", "timestamp": Decimal('1234349495'), "messages": [ { "role": "user", "content": "some content", "image": "base64" }, { "role": "assistant", "content": "some content from peer" }, { "role": "user", "content": "some content 2", "image": "" }, { "role": "assistant", "content": "some content from peer answer" } ] }
        self.assertDictEqual(result, expected)
        await self.connector.delete_chat_by_id(id,ts)

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
        self._insert_sample_data(self.chats_table, sample_chat_data)
        await self.connector.delete_chat_by_id(id, ts)
        result =  await self.connector.get_chat_by_id(id, ts)
        self.assertIsNone(result)

    async def test_get_user(self):
        email = "test2@example.com"
        result =  await self.connector.get_user(email)
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
        result =  await self.connector.get_chat_by_id(id, ts)
        expected = {'messages': [{'role': 'user', 'content': 'some content', 'image': 'base64'}, {'role': 'assistant', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 'randomUUID15', 'timestamp': Decimal('1234567789')}
        self.assertDictEqual(result, expected)
        await self.connector.delete_chat_by_id(id, ts)
