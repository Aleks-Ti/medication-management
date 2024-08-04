from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


@dataclass
class BotConfig:
    token: str | None = getenv("TOKEN")

    def __post_init__(self):
        required_vars = "token"
        if getattr(self, required_vars) is None:
            raise ValueError("Отсутствует токен для бота в окружении проекта. Добавьте его в .env файл.")


@dataclass
class PostgresConfig:
    name_db: str | None = getenv("PG_DB_NAME")
    user: str | None = getenv("PG_USER_NAME")
    password: str | None = getenv("PG_PASSWORD")
    port: str | None = getenv("PG_PORT")
    host: str | None = getenv("PG_HOST")
    driver: str = "asyncpg"
    database_system = "postgresql"

    def __post_init__(self):
        required_vars = ["name_db", "user", "password", "port", "host"]
        for var in required_vars:
            if getattr(self, var) is None:
                raise ValueError(
                    f"Нет переменной {var} для коннекта БД в окружении проекта.",
                )

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name_db,
        ).render_as_string(hide_password=False)


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
        connect = f"redis://{self.redis_host}/{self.db_num_for_aiogram}/{self.db_num_for_calery}"
        return connect


redis_conf = RedisConfig()
postgres_conf = PostgresConfig()
bot_conf = BotConfig()
