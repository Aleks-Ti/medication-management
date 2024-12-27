import logging

from aiogram.types import Message
from httpx._models import Response

from src.core.api_client import AbstractApiClient
from src.core.config import settings
from src.user.requests import UserApiClient


class UserService:
    def __init__(self, user_api_client: AbstractApiClient) -> None:
        self.user_api_client: UserApiClient = user_api_client

    async def get_or_create_user(self, message: Message) -> Response:
        path = settings.BASE_API_URL + "/user"
        logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + path)
        response: Response = await self.user_api_client.post_one(
            path,
            {
                "username": message.from_user.full_name,
                "tg_user_id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
            },
        )

        return response
