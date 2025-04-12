from components.database.DDBConnectorSync import DDBConnectorSync
from components.repository.Repository import Repository
from decimal import Decimal
from config import config as appconfig
import logging

from models.ChatModel import ChatModel
from models.UserModel import UserModel

logger = logging.getLogger("ChatGPT")


class DDBRepository(Repository):
    def __init__(self, chats_table=None, users_table=None) -> None:
        if not chats_table and not users_table:
            chats_table = appconfig.DDB_CHATS_TABLE
            users_table = appconfig.DDB_USERS_TABLE
        self.ddb_connector = DDBConnectorSync(
            chats_table=chats_table, users_table=users_table
        )

    async def get_chats_by_email(self, email: str) -> dict:
        chats = await self.ddb_connector.get_chats_by_email(email)
        return self.convert_decimal_to_int(chats)

    async def get_chats_by_email_paginated(
        self, email: str, *, last_eval_key: dict, limit: int, load_images: bool = False
    ) -> dict:
        results = await self.ddb_connector.get_chats_by_email_paginated(
            email,
            last_evaluated_key=last_eval_key,
            limit=limit,
            load_images=load_images,
        )
        chats = self.convert_decimal_to_int(results["items"])
        return {"chats": chats, "last_eval_key": results["last_eval_key"]}

    async def get_chat_by_id(self, id: str) -> dict:
        chat = await self.ddb_connector.get_chat_by_id(id)
        return self.convert_decimal_to_int(chat)

    async def delete_chat_by_id(self, id: str, timestamp: int = None):
        await self.ddb_connector.delete_chat_by_id(id, timestamp)

    async def get_user(self, email: str) -> UserModel | None:
        return await self.ddb_connector.get_user(email)

    async def store_chat(self, chats_info: ChatModel):
        logger.debug(f"Trying to store chat {chats_info}")
        if not chats_info.messages:
            logger.info("No messages to store")
            return
        await self.ddb_connector.store_chat(chats_info)

    def convert_decimal_to_int(self, data: dict) -> dict:
        if isinstance(data, Decimal):
            return int(data)
        elif isinstance(data, list):
            return [self.convert_decimal_to_int(item) for item in data]
        elif isinstance(data, dict):
            return {
                key: self.convert_decimal_to_int(value) for key, value in data.items()
            }
        return data
