import logging
import aioboto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

class DDBConnector:

    def __init__(self, chats_table: str, users_table: str):
        self.chats_table = chats_table
        self.users_table = users_table

    async def get_chats_by_email(self, email: str) -> dict:
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(self.chats_table)
            response = await table.query(
                IndexName='user_email-index',
                KeyConditionExpression=Key('user_email').eq(email)
            )
            return response.get('Items', [])

    async def get_chat_by_id(self, id: str) -> dict:
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(self.chats_table)
            response = await table.get_item(Key={'chat_id': id})
            return response.get('Item')

    async def delete_chat_by_id(self, id: str):
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(self.chats_table)
            await table.delete_item(Key={'chat_id': id})

    async def get_user(self, email: str):
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(self.users_table)
            response = await table.get_item(Key={'email': email})
            return response.get('Item')

    async def store_chat(self, chat: dict):
        session = aioboto3.Session()
        async with session.resource('dynamodb', region_name='eu-central-1') as client:
            table = await client.Table(self.chats_table)
            await table.put_item(Item=chat)