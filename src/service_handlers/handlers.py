import asyncio
import logging

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.user.dependencies import user_service as _user_service
from src.utils.buttons import BaseMenuKeyboard as bmk
from src.utils.buttons import MainKeyboard as mk

start_router = Router(name="start")


@start_router.message(Command(bmk.CANCEL))
@start_router.message((F.text.casefold() == mk.CANCEL) | (F.text == mk.CANCEL))
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды отмены."""
    try:
        current_state = await state.get_state()
        if current_state is not None:
            logging.info("Cancelling state %r", current_state)
            await state.clear()
            deleted_message = await message.answer("Операция отменена.")
            await asyncio.sleep(1.9)
            await message.chat.delete_message(deleted_message.message_id)
            await asyncio.sleep(0.5)
            await message.delete()
        else:
            deleted_message = await message.answer("Нет активных операций для отмены.")
            await asyncio.sleep(1.9)
            await message.chat.delete_message(deleted_message.message_id)
            await asyncio.sleep(0.5)
            await message.delete()
    except Exception as err:
        logging.exception(f"Error: command cancel - {err}")


@start_router.message(CommandStart())
async def send_welcome(message: Message):
    """
    Вызывается в случаем получения команды `/start`

    methods:
        get_or_create_user - создания юзера и занесения в базу данных.
    """

    _ = await _user_service().get_or_create_user(message)

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
        "Мы поможем вам отслеживать прием лекарст/витаминов/минералов/препаратов или просто не забыть выпить "
        "йогурта в обед для хорошего пищеварения!\nБот поможет ничего не забыть!\n\n"
        "Если хотите создать курс приема лекарств, выбирайте кнопку **{}**\n\n"
        "Можете посмотреть пройденный курсы и заметки по ним, выбирайте кнопку **{}**".format(
            message.from_user.username,
            mk.ADD_DRUG_REGIMEN,
            mk.ME_DRUG_REGIMEN,
        ),
        reply_markup=keyboard,
    )


@start_router.message(Command(bmk.HELP))
# @start_router.message((F.text.casefold() == bmk.HELP))
async def help_handler(message: types.Message):
    await message.answer(text="Справка по боту и пользованию")
