from components.database.DDBConnector import DDBConnector
from components.repository.Repository import Repository
from components.repository.User import User

class DDBRepository(Repository):

    def __init__(self) -> None:
        self.ddb_connector =  DDBConnector('', '') #TODO: gather them from  env variables?

    async def get_chats_by_email(self, email: str) -> dict:
        pass

    async def get_chats_by_id(self, id: int) -> dict:
        pass

    async def delete_chat_by_id(self, id: int):
        pass

    async def get_user(self, email: str) -> User:
        pass

    async def store_chat(self, chat: dict):
        pass

    def _from_ddb_to_normal_dict(self, ddb_dict: dict) -> dict:
        """Format dictionary that DynamoDB Schemas understand to a 'normal' dictionary that follows JSON format"""
        pass

    def _from_normal_to_ddb_dict(self, normal: dict) -> dict:
        """Format 'normal' JSON like dict to DynamoD Schema standard"""
        pass