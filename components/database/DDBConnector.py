import logging
import aioboto3

logger = logging.getLogger(__name__)

class DDBConnector:

    def __init__(self, chats_table: str, users_table: str):
        self.chats_table = chats_table
        self.users_table = users_table

    async def get_chats_by_email(self, email: str) -> dict:
        async with aioboto3.client('dynamodb') as client:
            response = await client.query(
            TableName=self.chats_table,
            KeyConditionExpression='user_email = :email',
            ExpressionAttributeValues={
                    ':email': {'S': email}
                }
            )
            return response.get('Items', [])

    async def get_chat_by_id(self, id: int) -> dict:
        async with aioboto3.client('dynamodb') as client:
            response = await client.get_item(TableName=self.chats_table, Key={'id': {'N': id}})
            return response.get('Item')

    async def delete_chat_by_id(self, id: int):
        async with aioboto3.client('dynamodb') as client:
            await client.delete_item(TableName=self.chats_table, Key={'id': {'N': id}})

    async def get_user(self, email: str):
        async with aioboto3.client('dynamodb') as client:
            response = await client.get_item(TableName=self.users_table, Key={'email': {'S': email}})
            return response.get('Item')

    async def store_chat(self, chat: dict):
        async with aioboto3.client('dynamodb') as client:
            await client.put_item(TableName=self.chats_table, Item=chat)