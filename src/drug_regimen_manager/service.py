from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.core.api_client import AbstractApiClient
from src.core.config import settings
from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
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
        await state.clear()  # обязательная чистка, потому что пользователь может на середине любого сценария, прийти сюда
        response = await self.manager_api_client.get_all(self.base_manager_url, message.from_user.id)
        user_message = ""
        manager_user_data_dict = response.json()

        alias_manager_number = 1
        for manager in manager_user_data_dict:
            # alias_for_buttons.append(manager[""])
            manager["alias_manager_number"] = alias_manager_number
            user_message += (
                f"# Курс №{alias_manager_number} - *{manager["name"]}*\n"
                f"Начало от *{datetime.fromisoformat(manager["start_date"][:-1] + '+00:00').strftime("%d.%m.%Y")}*\n"
                f"Окончание *{datetime.fromisoformat(manager["finish_date"][:-1] + '+00:00').strftime("%d.%m.%Y")}*\n"
                f"Выбранная временная зона {manager["timezone"] if manager["timezone"] == "МСК" else str(manager["timezone"]) + " часов от МСК"}\n"
            )
            alias_manager_number += 1

            alias_regimen_number = 1
            for regimen in manager["regimens"]:
                regimen["alias_regimen_number"] = alias_regimen_number
                user_message += (
                    f"\t\t`- Напоминание №`{alias_regimen_number} назначенное на: {regimen["reception_time"]}\n"
                    f"\t\t- - Стикер:\n\t\t\t\t\t\t{regimen["supplement"]}\n\n"
                )
                alias_regimen_number += 1
            user_message += "\n"
        if not user_message:
            await message.answer("У вас пока нет курсов.")
        else:
            await state.update_data(user_managers_data=manager_user_data_dict)
            save_message_data = await message.answer(
                "```md\n" + user_message + "```",
                parse_mode="MarkdownV2",
                reply_markup=await ibg.manager_inline_button(),
            )
            await state.update_data(previous_get_all_message_id=save_message_data.message_id)

    async def settings_manager(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_manager_data = await state.get_data()
        previous_get_all_message_id = temp_manager_data["previous_get_all_message_id"]
        new_inline_keyboard = await ibg.inline_buttons_generator(
            prefix="№",
            buttons=range(1, len(temp_manager_data["user_managers_data"]) + 1),
            callback_unique_indetifier="edit_manager_or_regimen_",
        )
        await callback_query.message.edit_reply_markup(
            inline_message_id=str(previous_get_all_message_id),
            reply_markup=new_inline_keyboard,
        )

    async def edit_manager(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_manager_data = await state.get_data()
        temp_managers = temp_manager_data["user_managers_data"]
        previous_get_all_message_id = temp_manager_data["previous_get_all_message_id"]
        await callback_query.message.chat.delete_message(previous_get_all_message_id)
        manager = temp_managers[int(callback_query.data.split("№")[-1]) - 1]  # по индексу достаю, потому что порядок заморожен, халява

        user_message = ""
        user_message += (
            f"# Курс №{manager["alias_manager_number"]} - *{manager["name"]}*\n"
            f"Начало от *{datetime.fromisoformat(manager["start_date"][:-1] + '+00:00').strftime("%d.%m.%Y")}*\n"
            f"Окончание *{datetime.fromisoformat(manager["finish_date"][:-1] + '+00:00').strftime("%d.%m.%Y")}*\n"
            f"Выбранная временная зона {manager["timezone"] if manager["timezone"] == "МСК" else str(manager["timezone"]) + " часов от МСК"}\n"
        )

        alias_regimen_number = 1
        count_regimen_for_manager = 0
        for regimen in manager["regimens"]:
            count_regimen_for_manager += 1
            regimen["alias_regimen_number"] = alias_regimen_number
            user_message += (
                f"\t\t`- Напоминание №`{alias_regimen_number} назначенное на: {regimen["reception_time"]}\n"
                f"\t\t- - Стикер:\n\t\t\t\t\t\t{regimen["supplement"]}\n\n"
            )
            alias_regimen_number += 1
        user_message += "\n"

        if count_regimen_for_manager == 0:
            regimen_inline_button_for_manager = False
        else:
            regimen_inline_button_for_manager = True

        save_message_data = await callback_query.message.answer(
            "```md\n" + user_message + "```",
            parse_mode="MarkdownV2",
            reply_markup=await ibg.manager_or_regimen_edit_inline_buttons(
                regimen_inline_button_for_manager,
                callback_query.data.split("№")[-1],
            ),
        )
        await state.update_data(previous_get_all_message_id=save_message_data.message_id)
