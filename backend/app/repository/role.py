from typing import List

from sqlalchemy.future import select

from app.config import session_scope
from app.model.role import Role
from app.repository.base_repo import BaseRepo


class RoleRepository(BaseRepo):
    model = Role

    @staticmethod
    async def find_by_role_name(role_name: str):
        async with session_scope() as session:
            query = select(Role).where(Role.role_name == role_name)
            return (await session.execute(query)).scalar_one_or_none()

    @staticmethod
    async def find_by_role_names(role_names: List[str]):
        async with session_scope() as session:
            query = select(Role).where(Role.role_name.in_(role_names))
            return (await session.execute(query)).scalars().all()

    @staticmethod
    async def create_list(roles: List[Role]):
        async with session_scope() as session:
            session.add_all(roles)
