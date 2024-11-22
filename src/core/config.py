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
    # db_num_for_calery: int = int(getenv("REDIS_DATABASE_FOR_CELERY", 1))  # 0-10
    db_num_for_aiogram: int = int(getenv("REDIS_DATABASE_FOR_AIOGRAM", 0))  # 0-10
    redis_host: str | None = "localhost" if os.getenv("DEV") == "local" else "host.docker.internal"  # getenv("REDIS_HOST", "localhost")

    password: str | None = getenv("REDIS_PASSWORD")
    port: str | None = getenv("REDIS_PORT")

    def __post_init__(self):
        required_vars = ["db_num_for_aiogram", "redis_host", "password", "port"]
        for var in required_vars:
            if getattr(self, var) is None:
                raise ValueError(
                    f"Нет переменной {var} для коннекта к Redis в окружении проекта.",
                )

    # def build_connection_str_for_celery(self) -> str:
    #     connect = f"redis://{self.redis_host}:{self.port}/{self.db_num_for_calery}"
    #     return connect

    def build_connection_str_for_aiogram(self) -> str:
        connect = f"redis://{self.redis_host}:{self.port}/{self.db_num_for_aiogram}"
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


@dataclass
class MQEnvs:
    ui_port: str | None = getenv("RMQ_UI_PORT")
    network_port: int | None = int(getenv("RMQ_NETWOTK_PORT"))
    user: str | None = str(getenv("RMQ_USERNAME"))
    password: str | None = str(getenv("RMQ_PASSWORD"))
    inner_port_for_compose: int = int(getenv("RMQ_UI_INNER_PORT"))
    rabbit_host: str = "localhost" if os.getenv("DEV") == "local" else "host.docker.internal"

    def __post_init__(self):
        required_vars = ["ui_port", "network_port", "user", "password", "inner_port_for_compose"]
        for var in required_vars:
            value = getattr(self, var)
            if value is None:
                raise ValueError(f"Environment variable for <{var}> is not set")

    def build_connection(self):
        import logging
        logging.info(f"!!!!!!!!!!!!!{self.rabbit_host}")
        return f"amqp://{self.user}:{self.password}@{self.rabbit_host}:{self.network_port}/"


redis_conf = RedisConfig()
bot_conf = BotConfig()
settings = Settings()
rabbit_mq = MQEnvs()
