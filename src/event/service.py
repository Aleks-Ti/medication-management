import asyncio
import json
import logging
from typing import NoReturn

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractQueue
from aiogram import Bot

from src.core.config import rabbit_mq


class EventService:
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    async def send_messages_users(self, message: str) -> None:
        message = message.replace("'", '"')
        message = json.loads(message)
        message_text = (
            f"```md\n# Привет!\n\nСпешу напомнить о {message["manager_name"]}:\n- Напоминание было назначенное на "
            f"*{message["reception_time"]}*.\n- Стикер >> *{message["supplement"]}*\n```"
        )
        await self.bot.send_message(chat_id=message["tg_user_id"], text=message_text, parse_mode="MarkdownV2")

    async def consume_from_rabbitmq(self) -> NoReturn:
        """
        Опрос очереди RabbitMQ.
        """
        while True:
            try:
                connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
                    rabbit_mq.build_connection(),
                )

                async with connection as conn:
                    channel: AbstractChannel = await conn.channel()

                    queue: AbstractQueue = await channel.declare_queue(
                        "dispatch_messages",  # имя очереди
                        durable=True,  # очередь устойчива к сбоя
                    )

                    async for message in queue:
                        try:
                            await self.send_messages_users(message.body.decode())
                            await message.ack()
                            logging.info("Успешно обработано сообщение из очереди.")
                        except Exception as err:
                            logging.error(f"Ошибка обработки сообщения: {err}")
                            # вернуть в очередь .nack(requeue=True)
                            await message.nack(requeue=True)
                            await asyncio.sleep(5)
            except Exception as err:
                logging.error(f"Ошибка при подключении к RabbitMQ или потере соединения: {err}")
                logging.info("Ожидаем 5 секунд и пробуем снова...")
                await asyncio.sleep(5)
