import logging
import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

class DDBConnectorSync:

    def __init__(self, chats_table: str, users_table: str):
        self.chats_table = chats_table
        self.users_table = users_table
        self.resource = boto3.resource("dynamodb")

    async def get_chats_by_email(self, email: str) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            response = table.query(
                IndexName='user_email-index',
                KeyConditionExpression=Key('user_email').eq(email)
            )
        except Exception as e:
            logger.error(f"Error querying for {email} {e}")
            return []
        return response.get('Items', [])

    async def get_chat_by_id(self, id: str, timestamp: int) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            response = table.get_item(Key={'chat_id': id, 'timestamp': timestamp})
        except Exception as e:
            logger.error(f"Error querying chat with id {id} {e}")
            return None
        return response.get('Item')

    async def delete_chat_by_id(self, id: str, timestamp: int):
        table = self.resource.Table(self.chats_table)
        try:
            response = table.delete_item(Key={'chat_id': id, 'timestamp': timestamp})
            logger.debug(f"Deleting ID {id}. Response: {response}")
        except Exception as e:
            logger.error(f"Error deleting chat with id {id} {e}")

    async def get_user(self, email: str):
        table = self.resource.Table(self.users_table)
        try:
            response = table.get_item(Key={'email': email})
        except Exception as e:
            logger.error(f"Error querying user with email {email} {e}")
            return None
        return response.get('Item')

    async def store_chat(self, chat: dict):
        table = self.resource.Table(self.chats_table)
        try:
            response = table.put_item(Item=chat)
            logger.debug(f"Created chat {chat}. Response: {response}")
        except Exception as e:
            logger.error(f"Error saving chat {chat} {e}")