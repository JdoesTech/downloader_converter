from sqlalchemy import update as sql_update
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.config import session_scope
from app.model.users import Users
from app.repository.base_repo import BaseRepo


class UsersRepository(BaseRepo):
    model = Users

    @staticmethod
    async def find_by_email(email: str):
        async with session_scope() as session:
            query = (
                select(Users)
                .options(selectinload(Users.roles))
                .where(Users.email == email)
            )
            return (await session.execute(query)).scalar_one_or_none()

    @staticmethod
    async def update_password(email: str, password: str):
        async with session_scope() as session:
            query = (
                sql_update(Users)
                .where(Users.email == email)
                .values(password=password)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
