import logging
from calendar import monthrange
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.core.api_client import AbstractApiClient
from src.core.config import settings
from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
from src.drug_regimen.state_machine import ManagerState, RegimenState
from src.drug_regimen.utils import LOCAL_RU_MONTH, get_user_date
from src.user.requests import UserApiClient
from src.utils.buttons import InlineButtonsGenerator as ibg
from src.utils.validate_user_message import validate_input

TEMP_DATA_FOR_MANAGER = "temp_data_with_date_for_user"


class DrManagerService:
    def __init__(
        self,
        manager_api_client: AbstractApiClient,
        regimen_api_client: AbstractApiClient,
        user_api_client: AbstractApiClient,
    ):
        self.manager_api_client: ManagerApiClient = manager_api_client
        self.regimen_api_client: RegimenApiClient = regimen_api_client
        self.user_api_client: UserApiClient = user_api_client
        self._validate_input = validate_input
        self.base_manager_url = settings.BASE_API_URL + "/drug-regimen/manager"
        self.base_regimen_url = settings.BASE_API_URL + "/drug-regimen/regimen"
        self.API_URL = settings.BASE_API_URL

    async def get_all_managers_for_user(self, message: types.Message, state: FSMContext):
        response = await self.manager_api_client.get_all(self.base_manager_url, message.from_user.id)
        user_message = ""
        for manager in response.json():
            user_message += (
                f"# Курс *{manager["name"]}*\n"
                f"Начало от *{manager["start_date"]}*\n"
                f"Окончание *{manager["finish_date"]}*\n"
                f"Выбранная временная зона {manager["timezone"] if manager["timezone"] == "`МСК`" else str(manager["timezone"]) + " часов от МСК"}\n"
            )
            count_li = 1
            for regimen in manager["regimens"]:
                user_message += (
                    f"\t\t{count_li} - напоминание в течении дня: {regimen["reception_time"]}\n"
                    f"\t\t- - дополнительное описание к напоминанию: {regimen["supplement"]}\n\n"
                )
                count_li += 1
            user_message += "\n"
        await message.answer(
            "```md\n" + user_message + "```",
            parse_mode="MarkdownV2",
        )
