from calendar import monthrange
from datetime import datetime, timedelta

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.core.api_client import AbstractApiClient
from src.core.config import settings
from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
from src.drug_regimen.state_machine import ManagerState, RegimenState
from src.drug_regimen.utils import LOCAL_RU_MONTH, get_user_date
from src.user.service import UserService
from src.utils.buttons import InlineButtonsGenerator as ibg

TEMP_DATA_FOR_MANAGER = "temp_data_with_date_for_user"


class ManagerService:
    async def survey_name(self, message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(ManagerState.name)
        await message.answer(
            "Придумайте название курсу приема лекарст.\nНазвание может быть произвольным. Главное чтобы вам было понятно.\n"
            "Кстати это может быть что угодно. Даже курс отжиманий! "
            "Но, расчитано всё таки со спецификой приема лекарст.\nТак же вкурсе может быть до "
            "пяти отслеживаний препаратов одновременно.",
        )

    async def survey_date(self, message: types.Message, state: FSMContext):
        await state.set_state(ManagerState.start_date)
        await state.update_data(plane_name=message.text)

        await message.delete()

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        current_month_name = LOCAL_RU_MONTH[current_month]
        next_month_name = None

        days_current_month = monthrange(current_year, current_month)[1]
        keyboard = await ibg.inline_buttons_generator(range(current_day, days_current_month + 1))
        keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])

        if len(keyboard.inline_keyboard) < 7:
            next_month = current_month + 1 if current_month < 12 else 1
            next_month_name = LOCAL_RU_MONTH[next_month]
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
            next_month_days = await ibg.inline_buttons_generator(range(1, days_current_month - current_day + 1))
            for day_keyboard_next_month in next_month_days.inline_keyboard:
                keyboard.inline_keyboard.append(day_keyboard_next_month)
        else:
            skip_row_name_math = 1
            max_row_buttons = 3
            keyboard.inline_keyboard = keyboard.inline_keyboard[: max_row_buttons + skip_row_name_math]
            keyboard.inline_keyboard[max_row_buttons + skip_row_name_math - 1].pop()
            keyboard.inline_keyboard[max_row_buttons + skip_row_name_math - 1].pop()

        temp_data_with_date_for_user = await ibg.get_string_representation_pool_inline_buttons(keyboard)
        await state.update_data(temp_data_with_date_for_user=temp_data_with_date_for_user)
        await message.answer(
            "Когда начнем? Запланируем старт ближайшую неделю. Сначала выберем подходящий день.",
            reply_markup=keyboard,
        )

    async def survey_finish_date(self, callback_query: types.CallbackQuery, state: FSMContext):
        if callback_query.data in LOCAL_RU_MONTH.values():  # NOTE заглушка, если пользователь протыкает название месяца, а не дату.
            await state.set_state(ManagerState.start_date)
            return

        data_state = await state.get_data()
        choice_start_date = data_state[TEMP_DATA_FOR_MANAGER]
        user_choice = callback_query.data

        start_date_plan_for_manager = await get_user_date(choice_start_date, user_choice)
        "which month the user selection belongs to"
        await state.update_data(start_date=start_date_plan_for_manager.strftime("%Y-%m-%d"))

        current_year = start_date_plan_for_manager.year
        current_day = start_date_plan_for_manager.day
        current_month = start_date_plan_for_manager.month

        next_30_days = []
        for i in range(30):
            new_date = start_date_plan_for_manager + timedelta(days=i)
            next_30_days.append(new_date.strftime("%Y-%m-%d"))

        current_month_name = LOCAL_RU_MONTH[current_month]
        days_current_month = monthrange(current_year, current_month)[1]
        keyboard = await ibg.inline_buttons_generator(range(current_day, days_current_month + 1))
        keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])

        if len(keyboard.inline_keyboard) < 30:
            use_count_days = days_current_month - current_day
            next_month = current_month + 1 if current_month < 12 else 1
            next_month_name = LOCAL_RU_MONTH[next_month]
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
            days_next_month = monthrange(current_year, next_month)[1]
            next_month_days = await ibg.inline_buttons_generator(range(1, days_next_month - use_count_days + 1))
            for day_keyboard_next_month in next_month_days.inline_keyboard:
                keyboard.inline_keyboard.append(day_keyboard_next_month)

        temp_data_with_date_for_user = await ibg.get_string_representation_pool_inline_buttons(keyboard)

        await state.update_data(temp_data_with_date_for_user=temp_data_with_date_for_user)
        await state.set_state(ManagerState.finish_date)
        await callback_query.message.delete()
        await callback_query.message.answer(
            "Теперь нужно выбрать, окончание курса приема лекарст. Заланируем на билжайший месяц. Но не более двух месяцев. "
            "Если вы собираетесь сделать такой длинный курс, то лучше"
            "соориентруйтесь на курс лекарств, и лучше перезапустите/повторите месячный курс по завершению первого.",
            reply_markup=keyboard,
        )

    async def survey_timezone(self, callback_query: types.CallbackQuery, state: FSMContext):
        await state.set_state(ManagerState.timezone)
        data_state = await state.get_data()

        choice_finish_date = data_state[TEMP_DATA_FOR_MANAGER]
        user_choice = callback_query.data
        finish_date_plan_for_manager = await get_user_date(choice_finish_date, user_choice)
        "which month the user selection belongs to"
        await state.update_data(finish_date=finish_date_plan_for_manager.strftime("%Y-%m-%d"))
        mask_buttons = [x if x != 0 else "МСК" for x in range(-1, 10)]
        keyboard = await ibg.inline_buttons_generator([x if isinstance(x, str) or x == -1 else "+" + str(x) for x in mask_buttons])
        await callback_query.message.delete()
        await callback_query.message.answer(
            "Давайте выберем часовой пояс! Чтобы было легче ориентироваться, оттолкнемся от московской времени.",
            reply_markup=keyboard,
        )


class RegimenService:
    def __init__(
        self,
        manager_api_client: AbstractApiClient,
        regimen_api_client: AbstractApiClient,
        user_service: UserService,
    ):
        self.manager_api_client: ManagerApiClient = manager_api_client
        self.regimen_api_client: RegimenApiClient = regimen_api_client
        self.user_service: UserService = user_service
        self.API_URL = settings.BASE_API_URL

    async def __add_full_plane_and_first_regimen_time(self, callback_query: types.CallbackQuery, state: FSMContext):
        state_data = await state.get_data()
        fields_for_manager = {
            "name": state_data["plane_name"],
            "start_date": datetime.strptime(state_data["start_date"], "%Y-%m-%d").strftime("%Y-%m-%d"),
            "finish_date": datetime.strptime(state_data["finish_date"], "%Y-%m-%d").strftime("%Y-%m-%d"),
            "timezone": state_data["timezone"],
            "is_active": True,
        }
        fields_for_regimen = {
            "reception_time": datetime.strptime(state_data["regimen_time"], "%H:%M").time().strftime("%H:%M"),
            "supplement": state_data["regimen_supplement"],
            "is_active": True,
        }
        body = {
            "user_tg_id": callback_query.from_user.id,
            "manager": fields_for_manager,
            "regimen": fields_for_regimen,
        }
        path = self.API_URL + "/drug-regimen/manager/complex"
        response_manager = await self.manager_api_client.post_one(body, path)
        await state.clear()
        await state.update_data(count_regimen=1)
        await state.update_data(manager_id=response_manager.json()["id"])

    async def __add_more_regimen_time(self, callback_query: types.CallbackQuery, state: FSMContext):
        state_data = await state.get_data()
        if state_data["count_regimen"] >= 10:
            raise

        body = {
            "manager_id": state_data["manager_id"],
            "supplement": state_data["regimen_supplement"],
            "is_active": True,
            "reception_time": datetime.strptime(state_data["regimen_time"], "%H:%M").time().strftime("%H:%M"),
        }
        path = self.API_URL + "/drug-regimen/regimen/complex"
        await self.manager_api_client.post_one(body, path)
        await state.update_data(count_regimen=state_data["count_regimen"] + 1)

    async def survey_regimen_time(self, callback_query: types.CallbackQuery, state: FSMContext):
        user_choice = callback_query.data
        await state.update_data(timezone=user_choice)
        await state.set_state(RegimenState.hour)
        keyboard = await ibg.inline_buttons_generator(range(0, 24), postfix=":xx")
        await callback_query.message.delete()
        await callback_query.message.answer(
            "Отлично! \nТеперь выберите время приема лекарства в течении дня.\nСначала выбере час, потом минуты. ",
            reply_markup=keyboard,
        )

    async def survey_regimen_hour(self, callback_query: types.CallbackQuery, state: FSMContext):
        user_choice = callback_query.data
        # await state.update_data(regimen_hour=user_choice)
        await state.set_state(RegimenState.regimen_time)
        keyboard = await ibg.inline_buttons_generator(
            [x if x >= 10 else "0" + str(x) for x in range(0, 56, 5)],
            prefix=user_choice.split(":")[0] + ":",
        )
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Хорошо?\nВыбран час {user_choice.split(":")[0]}:00.\nТеперь выберите минуты. ",
            reply_markup=keyboard,
        )

    async def survey_point_time(self, callback_query: types.CallbackQuery, state: FSMContext):
        user_choice = callback_query.data
        await state.update_data(regimen_time=user_choice)
        await state.set_state(RegimenState.supplement)
        await callback_query.message.delete()
        new_message = await callback_query.message.answer(
            "Прекрасно. Осталось к этому конкретному напоминанию добавить памятку.\n"
            "Например:\nПосле еды или до. Выпить тощак принять или запить обильным количество воды, может быть рассосать и тп.",
        )
        await state.update_data(previous_message_id=new_message.message_id)

    async def survey_supplement(self, message: types.Message, state: FSMContext):
        previous_message_id = (await state.get_data())["previous_message_id"]
        user_text = message.text
        await state.update_data(regimen_supplement=user_text)
        await state.set_state(RegimenState.add_more)
        await message.chat.delete_message(previous_message_id)
        await message.delete()
        await message.answer(
            "Добавить ещё время приема в течении дня?",
            reply_markup=await ibg.yes_or_not_inline_buttons(),
        )

    async def survey_add_more(self, callback_query: types.CallbackQuery, state: FSMContext):
        state_data = await state.get_data()
        # user_choice = callback_query.data
        # await state.update_data(regimen_supplement=user_choice)
        if callback_query.data == "yes":
            if state_data.get("count_regimen", False):
                await self.__add_more_regimen_time(callback_query, state)
            else:
                await self.__add_full_plane_and_first_regimen_time(callback_query, state)
            await state.set_state(RegimenState.hour)
            keyboard = await ibg.inline_buttons_generator(range(0, 24), postfix=":xx")
            await callback_query.message.delete()
            await callback_query.message.answer(
                "Выберите ещё одно время приема лекарства в течении дня.",
                reply_markup=keyboard,
            )
        else:
            if state_data.get("count_regimen", False):
                await self.__add_more_regimen_time(callback_query, state)
            else:
                await self.__add_full_plane_and_first_regimen_time(callback_query, state)
            await state.set_state(RegimenState.hour)
            await state.clear()
            await callback_query.message.delete()
            await callback_query.message.answer(
                "Данные сохранены в системе.",
            )
