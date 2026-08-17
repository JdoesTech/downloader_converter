from typing import Generic, TypeVar

from sqlalchemy import delete as sql_delete
from sqlalchemy import update as sql_update
from sqlalchemy.future import select

from app.config import session_scope

T = TypeVar("T")


class BaseRepo:
    model = Generic[T]

    @classmethod
    async def create(cls, **kwargs):
        async with session_scope() as session:
            model = cls.model(**kwargs)
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return model

    @classmethod
    async def get_all(cls):
        async with session_scope() as session:
            query = select(cls.model)
            return (await session.execute(query)).scalars().all()

    @classmethod
    async def get_by_id(cls, model_id: str):
        async with session_scope() as session:
            query = select(cls.model).where(cls.model.id == model_id)
            return (await session.execute(query)).scalar_one_or_none()

    @classmethod
    async def update(cls, model_id: str, **kwargs):
        async with session_scope() as session:
            query = (
                sql_update(cls.model)
                .where(cls.model.id == model_id)
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)

    @classmethod
    async def delete(cls, model_id: str):
        async with session_scope() as session:
            query = sql_delete(cls.model).where(cls.model.id == model_id)
            await session.execute(query)
