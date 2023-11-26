from components.database.DDBConnector import DDBConnector
from components.repository.Repository import Repository
from components.repository.User import User
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import os

class DDBRepository(Repository):

    def __init__(self) -> None:
        chats_table = os.env('DDB_CHATS_TABLE')
        users_table = os.env('DDB_USERS_TABLE')
        self.ddb_connector =  DDBConnector(chats_table=chats_table, users_table=users_table)

    async def get_chats_by_email(self, email: str) -> dict:
        chats = await self.ddb_connector.get_chats_by_email(email)
        chats_list = [self._from_ddb_to_normal_dict(chat) for chat in chats]
        return chats_list

    async def get_chat_by_id(self, id: int) -> dict:
        chat = await self.ddb_connector.get_chat_by_id(id)
        return self._from_ddb_to_normal_dict(chat)

    async def delete_chat_by_id(self, id: int):
        await self.ddb_connector.delete_chat_by_id(id)

    async def get_user(self, email: str) -> User:
        user = await self.ddb_connector.get_user(email)
        return self._from_ddb_to_normal_dict(user)

    async def store_chat(self, chat: dict):
        to_save_chat = self._from_normal_to_ddb_dict(chat)
        await self.ddb_connector.store_chat(to_save_chat)

    def _from_ddb_to_normal_dict(self, ddb_dict: dict) -> dict:
        if ddb_dict == None:
            return None
        deserializer = TypeDeserializer()
        return {k: deserializer.deserialize(v) for k, v in ddb_dict.items()}

    def _from_normal_to_ddb_dict(self, normal: dict) -> dict:
        if normal == None:
            return None
        serializer = TypeSerializer()
        return {k: serializer.deserialize(v) for k, v in normal.items()}