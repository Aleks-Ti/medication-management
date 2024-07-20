import logging

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.celery_tasks.tasks import send_reminder, send_reminder1
from src.user.dependencies import user_service as _user_service
from src.user.models import User
from src.utils.buttons import BaseMenuKeyboard as bmk
from src.utils.buttons import MainKeyboard as mk

start_router = Router(name="start")


@start_router.message(Command("cancel"))
@start_router.message((F.text.casefold() == mk.CANCEL) | (F.text == mk.CANCEL))
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды отмены."""
    try:
        current_state = await state.get_state()
        if current_state is not None:
            logging.info("Cancelling state %r", current_state)
            await state.clear()
            await message.answer("Операция отменена.")
        else:
            send_reminder.apply_async((message.from_user.id, "!!!!!!!!!!"), countdown=30)
            send_reminder.apply_async((message.from_user.id, "@@@@@@@@@@@@@"), countdown=15)
            await message.answer("Нет активных операций для отмены.")
    except Exception as err:
        logging.exception(f"Error: command cancel - {err}")


@start_router.message(CommandStart())
async def send_welcome(message: Message):
    """
    Вызывается в случаем получения команды `/start`

    methods:
        get_or_create_user - создания юзера и занесения в базу данных.
    """

    user: User = await _user_service().user_repository.get_or_create_user(message)

    button_1 = types.KeyboardButton(text=mk.ADD_DRUG_REGIMEN)
    button_2 = types.KeyboardButton(text=mk.ME_DRUG_REGIMEN)
    button_last = types.KeyboardButton(text=mk.CANCEL)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_last]],
        resize_keyboard=True,
    )

    await message.answer(
        text="Привет {}!\n"
        "Добро пожаловать в телеграм бота!\n"
        "Мы поможем вам отслеживать прием лекарст, чтобы ничего не забыть.\n\n"
        "Если хотите создать курс приема лекарств, выбирайте кнопку **{}**\n\n"
        "Можете посмотреть пройденный курсы и заметки по ним, выбирайте кнопку **{}**".format(
            user.first_name, mk.ADD_DRUG_REGIMEN, mk.ME_DRUG_REGIMEN,
        ),
        reply_markup=keyboard,
    )


@start_router.message(Command("help"))
@start_router.message((F.text.casefold() == bmk.HELP))
async def help_handler(message: types.Message):
    await message.answer(text="Справка по боту и пользованию")
