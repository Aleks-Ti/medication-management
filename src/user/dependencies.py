from src.user.requests import UserApiClient
from src.user.service import UserService


def user_service():
    return UserService(UserApiClient())
