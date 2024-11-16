import os
from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    token: str | None = getenv("TOKEN")

    def __post_init__(self):
        required_vars = "token"
        if getattr(self, required_vars) is None:
            raise ValueError("Отсутствует токен для бота в окружении проекта. Добавьте его в .env файл.")


@dataclass
class RedisConfig:
    db_num_for_calery: int = int(getenv("REDIS_DATABASE_FOR_CELERY", 0))  # 0-10
    db_num_for_aiogram: int = int(getenv("REDIS_DATABASE_FOR_AIOGRAM", 1))  # 0-10
    redis_host: str | None = getenv("REDIS_HOST", "localhost")

    password: str | None = getenv("REDIS_PASSWORD")
    port: str | None = getenv("REDIS_PORT")

    def __post_init__(self):
        required_vars = ["db_num_for_calery", "password", "db_num_for_aiogram", "port"]
        for var in required_vars:
            if getattr(self, var) is None:
                raise ValueError(
                    f"Нет переменной {var} для коннекта к Redis в окружении проекта.",
                )

    def build_connection_str_for_celery(self) -> str:
        connect = f"redis://{self.redis_host}:{self.port}/{self.db_num_for_calery}"
        return connect

    def build_connection_str_for_aiogram(self) -> str:
        connect = f"redis://{self.redis_host}:{self.port}/{self.db_num_for_calery}"
        return connect


@dataclass
class Settings:
    BASE_API_URL = (
        os.getenv("BASE_URL_API_LOCAL")
        if os.getenv("DEV") == "local"
        else os.getenv("BASE_URL_API_CONTAINER")
        if os.getenv("DEV") == "local_container"
        else os.getenv("BASE_URL_API_PROD")
        if os.getenv("DEV") == "prod"
        else "Зайди в .env и Добавь DEV переменную и что нибудь из этого [BASE_URL_API_LOCAL, BASE_URL_API_CONTAINER, BASE_URL_API_PROD]"  # noqa
    )


redis_conf = RedisConfig()
bot_conf = BotConfig()
settings = Settings()
