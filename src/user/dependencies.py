from src.user.repository import UserRepository
from src.user.service import UserService


def user_service():
    return UserService(UserRepository)
