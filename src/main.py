import asyncio
import logging
import subprocess
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.core.config import bot_conf
from src.routers import all_routers
from src.utils.buttons import BOT_MENU_COMMANDS

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    # filename=os.path.join(os.path.dirname(__file__), "program.log"),
    encoding="utf-8",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"))

logging.getLogger().addHandler(console_handler)


async def main() -> None:
    try:
        bot = Bot(bot_conf.token)
        dp = Dispatcher()
        for router in all_routers:
            dp.include_router(router)
        await bot.set_my_commands(BOT_MENU_COMMANDS, language_code="ru")
        await dp.start_polling(bot)
    except Exception as err:
        logging.exception(f"Error. {err}")


if __name__ == "__main__":
    try:
        subprocess.run("alembic upgrade head", shell=True, check=True)
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Ручная остановка программы.")
    except Exception as err:
        logging.exception(f"Error. {err}")
