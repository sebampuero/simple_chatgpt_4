from components.repository.Repository import Repository
from sanic import Sanic
from constants.AppConstants import AppConstants

class Login:

    def __init__(self, repo: Repository) -> None:
        self.app =  Sanic.get_app(AppConstants.APP_NAME)
        self.repo = repo

    async def check_user_is_authorized(self,email: str) -> bool:
        return not await self.repo.get_user(email) == None