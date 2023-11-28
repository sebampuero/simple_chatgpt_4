from components.database.DDBConnector import DDBConnector
from components.repository.Repository import Repository
from components.repository.User import User
from decimal import Decimal
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

class DDBRepository(Repository):

    def __init__(self, chats_table=None, users_table=None) -> None:
        if not chats_table and not users_table:
            chats_table = os.getenv('DDB_CHATS_TABLE')
            users_table = os.getenv('DDB_USERS_TABLE')
        self.ddb_connector =  DDBConnector(chats_table=chats_table, users_table=users_table)

    async def get_chats_by_email(self, email: str) -> dict:
        chats = await self.ddb_connector.get_chats_by_email(email)
        return self.convert_decimal_to_int(chats)

    async def get_chat_by_id(self, id: str, timestamp: int = None) -> dict:
        chat = await self.ddb_connector.get_chat_by_id(id, timestamp)
        return self.convert_decimal_to_int(chat)

    async def delete_chat_by_id(self, id: str, timestamp: int = None):
        await self.ddb_connector.delete_chat_by_id(id, timestamp)

    async def get_user(self, email: str) -> User:
        return await self.ddb_connector.get_user(email)

    async def store_chat(self, chats: list, user_email: str, chat_id: str):
        if len(chats) == 0:
            logger.info("No messages to store")
            return
        if user_email.strip() == '':
            logger.info("Cannot store chats without email")
            return
        new_chat = {
            'chat_id': str(uuid.uuid4()) if chat_id == '' else chat_id,
            'timestamp': int(datetime.now().timestamp()),
            'user_email': user_email,
            'messages': chats
        }
        await self.ddb_connector.store_chat(new_chat)

    def convert_decimal_to_int(self, data):
        if isinstance(data, Decimal):
            return int(data)
        elif isinstance(data, list):
            return [self.convert_decimal_to_int(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.convert_decimal_to_int(value) for key, value in data.items()}
        return data