from src.core.repository import AbstractRepository
from src.user.repository import UserRepository


class UserService:
    def __init__(self, user_repository: AbstractRepository):
        self.user_repository: UserRepository = user_repository()
