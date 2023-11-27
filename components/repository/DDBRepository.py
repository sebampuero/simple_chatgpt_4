from components.database.DDBConnector import DDBConnector
from components.repository.Repository import Repository
from components.repository.User import User
from decimal import Decimal
import os

class DDBRepository(Repository):

    def __init__(self, chats_table=None, users_table=None) -> None:
        if not chats_table and not users_table:
            chats_table = os.env('DDB_CHATS_TABLE')
            users_table = os.env('DDB_USERS_TABLE')
        self.ddb_connector =  DDBConnector(chats_table=chats_table, users_table=users_table)

    async def get_chats_by_email(self, email: str) -> dict:
        return await self.ddb_connector.get_chats_by_email(email)

    async def get_chat_by_id(self, id: int, timestamp: int = None) -> dict:
        return await self.ddb_connector.get_chat_by_id(id, timestamp)

    async def delete_chat_by_id(self, id: int, timestamp: int = None):
        await self.ddb_connector.delete_chat_by_id(id, timestamp)

    async def get_user(self, email: str) -> User:
        return await self.ddb_connector.get_user(email)

    async def store_chat(self, chat: dict):
        await self.ddb_connector.store_chat(chat)

    def convert_decimal_to_int(self, data):
        if isinstance(data, Decimal):
            return int(data)
        elif isinstance(data, list):
            return [self.convert_decimal_to_int(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.convert_decimal_to_int(value) for key, value in data.items()}
        return data