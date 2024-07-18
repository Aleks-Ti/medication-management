import asyncio
import logging
import os
import subprocess
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv

from src.user.dependencies import user_service as _user_service
from src.user.models import User
from src.utils.buttons import MainKeyboard as mk

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    level=logging.ERROR,
    filename=os.path.join(os.path.dirname(__file__), "program.log"),
    encoding="utf-8",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"))

logging.getLogger().addHandler(console_handler)

dp = Dispatcher()

if token := os.getenv("TOKEN", default=False):
    TELEGRAM_TOKEN = token
else:
    raise ValueError("Нет переменной << TOKEN >> в .env файле для бота телеграма.")


@dp.message(Command("cancel"))
@dp.message((F.text.casefold() == mk.cancel) | (F.text == mk.cancel))
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды отмены."""
    try:
        current_state = await state.get_state()
        if current_state is not None:
            logging.info("Cancelling state %r", current_state)
            await state.clear()
            await message.answer("Операция отменена.")
        else:
            await message.answer("Нет активных операций для отмены.")
    except Exception as err:
        logging.exception(f"Error: command cancel - {err}")


@dp.message(CommandStart())
async def send_welcome(message: Message):
    """
    Вызывается в случаем получения команды `/start`

    methods:
        get_or_create_user - создания юзера и занесения в базу данных.
    """

    user: User = await _user_service().user_repository.get_or_create_user(message)

    button_1 = types.KeyboardButton(text=mk.ADD_DRUG_REGIMEN)
    button_2 = types.KeyboardButton(text=mk.ME_DRUG_REGIMEN)
    button_last = types.KeyboardButton(text=mk.cancel)
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


async def main() -> None:
    try:
        bot = Bot(TELEGRAM_TOKEN)
        await dp.start_polling(bot)
    except Exception as err:
        logging.exception(f"Error. {err}")


if __name__ == "__main__":
    try:
        subprocess.run("alembic upgrade head", shell=True, check=True)
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ручная остановка программы.")
    except Exception as err:
        logging.exception(f"Error. {err}")
