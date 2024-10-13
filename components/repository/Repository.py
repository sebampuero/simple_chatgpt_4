from typing import Protocol
from components.repository.User import User

class Repository(Protocol):
    """
    Interface to a repository, connects to the main datasource
    """
    
    async def get_chats_by_email(self, email: str) -> dict:
        pass

    async def get_chats_by_email_paginated(self, email: str, *, last_eval_key: dict, limit: int, load_images: bool = False) -> dict:
        pass

    async def get_chat_by_id(self, id: str,  timestamp: int = None) -> dict:
        pass

    async def delete_chat_by_id(self, id: str,  timestamp: int = None):
        pass

    async def get_user(self, email: str) -> User:
        pass

    async def store_chat(self, chat: dict):
        pass