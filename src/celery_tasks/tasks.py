import logging

import requests
from aiogram import Bot
from celery import Celery

from src.core.config import bot_conf, redis_conf

BOT = Bot(bot_conf.token)

celery = Celery("tasks", broker=redis_conf.build_connection_str_for_celery())


@celery.task
def send_reminder(chat_id: int, text):
    logging.info("Задача send_reminder запущена")
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    telegram_url = f"https://api.telegram.org/bot{bot_conf.token}/sendMessage"
    request = requests.post(telegram_url, json=data)
    print(request.status_code)
    print(request.text)
