from components.database.Database import Database
from components.repository.User import User

class CodeRepository:
    def __init__(self, database: Database):
        self.db = database

    def get_user_by_email(self, email: str) -> User:
        pass
