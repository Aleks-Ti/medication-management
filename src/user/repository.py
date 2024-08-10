from aiogram.types import Message
from sqlalchemy import insert, select

from src.core.postgres_connect import async_session_maker
from src.core.repository import SQLAlchemyRepository
from src.user.models import User


class UserRepository(SQLAlchemyRepository):
    model: type[User] = User

    async def get_or_create_user(self, message: Message) -> User:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.tg_user_id == message.from_user.id)
            result = (await session.execute(stmt)).scalar_one_or_none()
            if result is None:
                user_data = {
                    "username": message.from_user.full_name,
                    "tg_user_id": message.from_user.id,
                    "first_name": message.from_user.first_name,
                    "last_name": message.from_user.last_name,
                }

                stmt_user = insert(self.model).values(**user_data).returning(self.model)
                result_user = await session.execute(stmt_user)
                await session.commit()
                result = result_user.scalar_one()

            return result
