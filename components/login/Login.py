from components.repository.Repository import Repository
from components.repository.DDBRepository import DDBRepository
from sanic import Sanic
from constants.AppConstants import AppConstants


class Login:
    def __init__(self, repo: Repository = None) -> None:
        self.app = Sanic.get_app(AppConstants.APP_NAME)
        self.repo = DDBRepository() if not repo else repo

    async def check_user_is_authorized(self, email: str) -> bool:
        return not await self.repo.get_user(email) == None
