from calendar import monthrange
from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.drug_regimen.state_machine import ManagerState
from src.utils.buttons import MainKeyboard as mk
from src.utils.buttons import inline_buttons_generator

# from src.drug_regimen.buttons import drug_regimen_buttons

drug_regimen_router = Router(name="drug_regimen")

LOCAL_RU_MONTH = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}


@drug_regimen_router.message(F.text == mk.ADD_DRUG_REGIMEN)
# @drug_regimen_router.message(Command(mk.ADD_DRUG_REGIMEN))
async def manager_start_choice(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ManagerState.name)
    await message.answer(
        "Придумайте название курсу приема лекарст. Кстати это может быть что угодно. Даже курс отжиманий! "
        "Но, расчитано всё таки со спецификой приема лекарст.\nТак же вкурсе может быть до "
        "пяти отслеживаний препаратов одновременно.",
    )


@drug_regimen_router.message(ManagerState.name)
async def manager_start_date(message: types.Message, state: FSMContext):
    await state.set_state(ManagerState.start_date)
    current_date = datetime.now()
    current_year = current_date.year

    current_month = current_date.month
    current_month_name = LOCAL_RU_MONTH[current_month]

    current_day = current_date.day
    days_current_month = monthrange(current_year, current_month)[1]
    keyboard = await inline_buttons_generator(range(current_day, days_current_month + 1))
    keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])
    choice_user_date_for_manager = {
        current_month: [x[0].text for x in keyboard.inline_keyboard if x[0].text not in [x for x in LOCAL_RU_MONTH.values()]],
    }
    if len(keyboard.inline_keyboard) < 7:
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_name = LOCAL_RU_MONTH[next_month]
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
        next_month_days = await inline_buttons_generator(range(1, days_current_month - current_day + 1))
        for day_keyboard_next_month in next_month_days.inline_keyboard:
            keyboard.inline_keyboard.append(day_keyboard_next_month)
        choice_user_date_for_manager.update(
            {next_month: [x[0].text for x in keyboard.inline_keyboard if x[0].text not in [x for x in LOCAL_RU_MONTH.values()]]},
        )

    await state.update_data(choice_user_date_for_manager=choice_user_date_for_manager)
    await message.answer(
        "Когда начнем? Запланируем старт ближайшую неделю. Сначала выберем подходящий день.",
        reply_markup=keyboard,
    )


@drug_regimen_router.callback_query(ManagerState.start_date)
async def manager_set_start_date(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data in LOCAL_RU_MONTH.values():
        await state.set_state(ManagerState.start_date)
        return
    await state.set_state(ManagerState.finish_date)
    await callback_query.message.answer(
        "Теперь нужно выбрать, окончание курса приема лекарст. Заланируем на билжайший месяц. Но не более двух месяцев. "
        "Если вы собираетесь сделать такой длинный курс, то лучше"
        "соориентруйтесь на курс лекарств, и лучше перезапустите/повторите месячный курс по завершению первого.",
    )


@drug_regimen_router.message(ManagerState.finish_date)
async def manager_finish_date(message: types.Message, state: FSMContext):
    # NOTE начать генерацию кнопок не с текущей даты, а с даты начала курса. А скорей всего придется отдавать сначала число на выбор
    # TODO дохера продумать нужно на самом деле. Пора спать. Код ниже копипаст.
    await state.set_state(ManagerState.start_date)
    current_date = datetime.now()
    current_year = current_date.year

    current_month = current_date.month
    current_month_name = LOCAL_RU_MONTH[current_month]

    current_day = current_date.day
    days_current_month = monthrange(current_year, current_month)[1]
    keyboard = await inline_buttons_generator(range(current_day, days_current_month + 1))
    keyboard.inline_keyboard.insert(0, [types.InlineKeyboardButton(text=current_month_name, callback_data=current_month_name)])
    choice_user_date_for_manager = {
        current_month: [x[0].text for x in keyboard.inline_keyboard if x[0].text not in [x for x in LOCAL_RU_MONTH.values()]],
    }
    if len(keyboard.inline_keyboard) < 7:
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_name = LOCAL_RU_MONTH[next_month]
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=next_month_name, callback_data=next_month_name)])
        next_month_days = await inline_buttons_generator(range(1, days_current_month - current_day + 1))
        for day_keyboard_next_month in next_month_days.inline_keyboard:
            keyboard.inline_keyboard.append(day_keyboard_next_month)
        choice_user_date_for_manager.update(
            {next_month: [x[0].text for x in keyboard.inline_keyboard if x[0].text not in [x for x in LOCAL_RU_MONTH.values()]]},
        )

    await state.update_data(choice_user_date_for_manager=choice_user_date_for_manager)
    await message.answer(
        "Когда начнем? Запланируем старт ближайшую неделю. Сначала выберем подходящий день.",
        reply_markup=keyboard,
    )
