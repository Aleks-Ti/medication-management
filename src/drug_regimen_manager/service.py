from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.core.api_client import AbstractApiClient
from src.core.config import settings
from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
from src.drug_regimen_manager.state_machine import UpdateRegimenStiker, UpdateRegimenTime
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
        self.parse_mode = "MarkdownV2"

    @staticmethod
    async def __save_previous_message(state: FSMContext, message_id: int):
        await state.update_data(previous_settings_message_id=message_id)

    @staticmethod
    async def __delete_previous_message(callback_query: types.CallbackQuery, state: FSMContext):
        temp_manager_data = await state.get_data()
        previous_settings_message_id = temp_manager_data["previous_settings_message_id"]
        await callback_query.message.chat.delete_message(previous_settings_message_id)

    @staticmethod
    async def __get_previous_message(state: FSMContext) -> int:
        temp_manager_data = await state.get_data()
        return temp_manager_data["previous_settings_message_id"]

    async def get_all_managers_for_user(self, message: types.Message, state: FSMContext, user_tg_id: int = None):
        await state.clear()  # обязательная чистка, потому что пользователь может на середине любого сценария, прийти сюда
        response = await self.manager_api_client.get_all(self.base_manager_url, user_tg_id if user_tg_id else message.from_user.id)
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
                parse_mode=self.parse_mode,
                reply_markup=await ibg.manager_inline_button(),
            )
            await self.__save_previous_message(state, save_message_data.message_id)

    async def settings_manager(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_manager_data = await state.get_data()
        previous_settings_message_id = temp_manager_data["previous_settings_message_id"]
        new_inline_keyboard = await ibg.inline_buttons_generator(
            prefix="№",
            buttons=range(1, len(temp_manager_data["user_managers_data"]) + 1),
            callback_unique_indetifier="edit_manager_",
            prefix_mask="Курс ",
        )
        await callback_query.message.edit_reply_markup(
            inline_message_id=str(previous_settings_message_id),
            reply_markup=new_inline_keyboard,
        )

    async def choice_manager(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_managers_data = await state.get_data()
        temp_managers = temp_managers_data["user_managers_data"]
        await self.__delete_previous_message(callback_query, state)

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
            reply_markup=await ibg.delete_manager_or_regimen_edit_inline_buttons(
                regimen_inline_button_for_manager,
                callback_query.data.split("№")[-1],
            ),
        )
        await self.__save_previous_message(state, save_message_data.message_id)

    async def delete_manager(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_user_data = await state.get_data()
        temp_managers = temp_user_data["user_managers_data"]
        manager = temp_managers[int(callback_query.data.split("№")[-1]) - 1]  # по индексу достаю, потому что порядок заморожен, халява
        await self.manager_api_client.delete_one(self.base_manager_url, manager["id"])
        await self.__delete_previous_message(callback_query, state)
        await self.get_all_managers_for_user(callback_query.message, state, callback_query.from_user.id)

    async def choice_regimens(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_managers_data = await state.get_data()
        temp_managers = temp_managers_data["user_managers_data"]

        previous_settings_message_id = self.__get_previous_message(state)

        manager = temp_managers[int(callback_query.data.split("№")[-1]) - 1]
        new_inline_keyboard = await ibg.inline_buttons_generator(
            prefix="№",
            buttons=range(1, len(manager["regimens"]) + 1),
            callback_unique_indetifier="edit_regimen_",
            prefix_mask="Напоминание ",
        )
        await state.update_data(current_manager_for_edit_regimens=manager)
        await callback_query.message.edit_reply_markup(
            inline_message_id=str(previous_settings_message_id),
            reply_markup=new_inline_keyboard,
        )

    async def edit_regimen(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        temp_managers_data = await state.get_data()
        current_manager = temp_managers_data["current_manager_for_edit_regimens"]
        current_regimen = current_manager["regimens"][int(callback_query.data.split("№")[-1]) - 1]

        await state.update_data(current_edit_regimens=current_regimen)

        previous_settings_message_id = self.__get_previous_message(state)

        new_inline_keyboard = await ibg.edit_regimen_values_inline_button()

        text = (
            f"Какой параметр хотите отредактировать?\n- Напоминание назначенное на: "
            f"{current_regimen["reception_time"]}\n- - Стикер:\n\t\t\t\t{current_regimen["supplement"]}"
        )
        await callback_query.message.edit_text(
            text="```md\n" + text + "```",
            inline_message_id=str(previous_settings_message_id),
            parse_mode=self.parse_mode,
        )
        await callback_query.message.edit_reply_markup(
            inline_message_id=str(previous_settings_message_id),
            reply_markup=new_inline_keyboard,
        )

    async def survey_regimen_hour(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        await state.set_state(UpdateRegimenTime.hour)
        keyboard = await ibg.inline_buttons_generator(range(0, 24), postfix=":xx")
        await callback_query.message.delete()
        await callback_query.message.answer(
            "Отлично! \nТеперь измените время напоминания в течении дня.\nСначала час, потом минуты. ",
            reply_markup=keyboard,
        )

    async def survey_regimen_minute(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        user_choice = callback_query.data
        await state.set_state(UpdateRegimenTime.minute)
        keyboard = await ibg.inline_buttons_generator(
            [x if x >= 10 else "0" + str(x) for x in range(0, 56, 5)],
            prefix=user_choice.split(":")[0] + ":",
        )
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Хорошо?\nВыбран час {user_choice.split(":")[0]}:00.\nТеперь выберите минуты. ",
            reply_markup=keyboard,
        )

    async def update_regimen_time(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        user_choice_full_time = callback_query.data
        temp_user_data = await state.get_data()
        current_regimen = temp_user_data["current_edit_regimens"]
        await self.regimen_api_client.update_one(
            self.base_regimen_url,
            current_regimen["id"],
            {"reception_time": datetime.strptime(user_choice_full_time, "%H:%M").time().strftime("%H:%M")},
        )
        await callback_query.answer(f"Время для напоминания, изменено на {user_choice_full_time}", show_alert=True)
        await callback_query.message.delete()
        await self.get_all_managers_for_user(callback_query.message, state, callback_query.from_user.id)

    async def edit_regimen_stiker(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        await callback_query.message.delete()
        await state.set_state(UpdateRegimenStiker.value)
        message = await callback_query.message.answer(
            "Напишите новую заметку к напоминанию:",
        )
        await self.__save_previous_message(state, message.message_id)

    async def update_regimen_stiker(self, message: types.Message, state: FSMContext) -> None:
        if not self._validate_input(message.text):
            await message.reply("Ваш ввод содержит недопустимые символы | стикеры | гифки. Пожалуйста, попробуйте снова.")
            await state.set_state(UpdateRegimenStiker.value)
            return

        temp_manager_data = await state.get_data()
        previous_settings_message_id = temp_manager_data["previous_settings_message_id"]
        current_regimen = temp_manager_data["current_edit_regimens"]

        await self.regimen_api_client.update_one(self.base_regimen_url, current_regimen["id"], {"supplement": message.text})

        await message.chat.delete_message(previous_settings_message_id)

        await message.delete()
        await self.get_all_managers_for_user(message, state, message.from_user.id)
