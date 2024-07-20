from aiogram import Bot, types
from aiogram.enums import ParseMode

from src.core.celery_connect import celery
from src.core.config import bot_conf


@celery.task
def send_reminder(message: types.Message, text):
    bot = Bot(bot_conf.token, parse_mode=ParseMode.HTML)
    bot.send_message(chat_id=message.from_user.id, text=text)
