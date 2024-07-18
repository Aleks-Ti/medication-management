from aiogram.types import Message
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from src.core.database import async_session_maker
from src.core.repository import SQLAlchemyRepository
from src.user.models import User


class UserRepository(SQLAlchemyRepository):
    model: type[User] = User

    async def get_or_create_user(self, message: Message) -> User:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.tg_user_id == message.from_user.id)
            res = (await session.execute(stmt)).scalar_one_or_none()
            if res:
                return res
            else:
                user_data = {
                    "username": message.from_user.full_name,
                    "tg_user_id": message.from_user.id,
                    "first_name": message.from_user.first_name,
                    "last_name": message.from_user.last_name,
                }

                stmt_user = insert(User).values(**user_data).returning(User)
                res_user = await session.execute(stmt_user)
                await session.flush()
                user = res_user.scalar_one()
                # stmt_game_profile = insert(GameProfile).values({"user_id": user.id})
                # await session.execute(stmt_game_profile)

                # stmt = select(User).where(message.from_user.id == User.tg_user_id).options(selectinload(User.game_profile))
                # user = await session.execute(stmt)
                await session.commit()
                return user
