from calendar import monthrange
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.drug_regimen.state_machine import DrugState, ManagerState
from src.drug_regimen.utils import LOCAL_RU_MONTH, get_user_date
from src.utils.buttons import MainKeyboard as mk
from src.utils.buttons import get_string_representation_pool_inline_buttons, inline_buttons_generator

drug_regimen_router = Router(name="drug_regimen")

TEMP_DATA_FOR_MANAGER = "temp_data_with_date_for_user"


@drug_regimen_router.message(F.text == mk.ADD_DRUG_REGIMEN)
async def manager_start_choice(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ManagerState.name)
    await message.answer(
        "Придумайте название курсу приема лекарст.\nНазвание может быть произвольным. Главное чтобы вам было понятно.\n"
        "Кстати это может быть что угодно. Даже курс отжиманий! "
        "Но, расчитано всё таки со спецификой приема лекарст.\nТак же вкурсе может быть до "
        "пяти отслеживаний препаратов одновременно.",
    )


@drug_regimen_router.message(ManagerState.name)
async def manager_start_date(message: types.Message, state: FSMContext):
    await state.set_state(ManagerState.start_date)
    await state.update_data(plane_name=message.text)

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    current_month_name = LOCAL_RU_MONTH[current_month]
    next_month_name = None

    days_current_month = monthrange(current_year, current_month)[1]
    keyboard = await inline_buttons_generator(range(current_day, days_current_month + 1))
    keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])

    if len(keyboard.inline_keyboard) < 7:
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_name = LOCAL_RU_MONTH[next_month]
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
        next_month_days = await inline_buttons_generator(range(1, days_current_month - current_day + 1))
        for day_keyboard_next_month in next_month_days.inline_keyboard:
            keyboard.inline_keyboard.append(day_keyboard_next_month)
    else:
        skip_row_name_math = 1
        max_row_buttons = 3
        keyboard.inline_keyboard = keyboard.inline_keyboard[:max_row_buttons + skip_row_name_math]
        keyboard.inline_keyboard[max_row_buttons + skip_row_name_math - 1].pop()
        keyboard.inline_keyboard[max_row_buttons + skip_row_name_math - 1].pop()

    temp_data_with_date_for_user = await get_string_representation_pool_inline_buttons(keyboard)
    await state.update_data(temp_data_with_date_for_user=temp_data_with_date_for_user)
    await message.answer(
        "Когда начнем? Запланируем старт ближайшую неделю. Сначала выберем подходящий день.",
        reply_markup=keyboard,
    )


@drug_regimen_router.callback_query(ManagerState.start_date)
async def manager_survey_finish_date(callback_query: types.CallbackQuery, state: FSMContext):
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
    keyboard = await inline_buttons_generator(range(current_day, days_current_month + 1))
    keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])

    if len(keyboard.inline_keyboard) < 30:
        use_count_days = days_current_month - current_day
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_name = LOCAL_RU_MONTH[next_month]
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
        days_next_month = monthrange(current_year, next_month)[1]
        next_month_days = await inline_buttons_generator(range(1, days_next_month - use_count_days + 1))
        for day_keyboard_next_month in next_month_days.inline_keyboard:
            keyboard.inline_keyboard.append(day_keyboard_next_month)

    temp_data_with_date_for_user = await get_string_representation_pool_inline_buttons(keyboard)

    await state.update_data(temp_data_with_date_for_user=temp_data_with_date_for_user)
    await state.set_state(ManagerState.finish_date)
    await callback_query.message.answer(
        "Теперь нужно выбрать, окончание курса приема лекарст. Заланируем на билжайший месяц. Но не более двух месяцев. "
        "Если вы собираетесь сделать такой длинный курс, то лучше"
        "соориентруйтесь на курс лекарств, и лучше перезапустите/повторите месячный курс по завершению первого.",
        reply_markup=keyboard,
    )


@drug_regimen_router.callback_query(ManagerState.finish_date)
async def manager_finish_date(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerState.timezone)
    data_state = await state.get_data()

    choice_finish_date = data_state[TEMP_DATA_FOR_MANAGER]
    user_choice = callback_query.data
    finish_date_plan_for_manager = await get_user_date(choice_finish_date, user_choice)
    "which month the user selection belongs to"
    await state.update_data(finish_date=finish_date_plan_for_manager.strftime("%Y-%m-%d"))
    mask_buttons = [x if x != 0 else "МСК" for x in range(-1, 10)]
    keyboard = await inline_buttons_generator([x if isinstance(x, str) or x == -1 else "+" + str(x) for x in mask_buttons])
    await callback_query.message.answer(
        "Давайте выберем часовой пояс! Чтобы было легче ориентироваться, оттолкнемся от московской времени.",
        reply_markup=keyboard,
    )


# NOTE Кажется избыточным, лучше разбить нах 1 курс 1 лекартсво, пусть лучше заведут 5 таких курсов,
# чем это будет бесконечное добавление одного за другим лекарства в один курс.
@drug_regimen_router.callback_query(ManagerState.timezone)
async def manager_timezone(callback_query: types.CallbackQuery, state: FSMContext):
    user_choice = callback_query.data
    await state.update_data(timezone=user_choice)
    await state.set_state(DrugState.name)
    await callback_query.message.answer(
        "Отлично! С временными рамками мы определились!\nТеперь введите название лекарства в рамках курса.",
    )


@drug_regimen_router.callback_query(DrugState.name)
async def manager_drug_name(callback_query: types.CallbackQuery, state: FSMContext):
    user_text = callback_query.data
    await state.update_data(drug_name=user_text)
    await state.set_state(DrugState.start_date)
    await callback_query.message.answer(
        "Временные рамки в рамках курса?\nВыберете дату начала приема препарата в рамках курса. ",
    )
