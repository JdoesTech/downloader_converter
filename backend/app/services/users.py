from sqlalchemy.future import select

from app.config import session_scope
from app.model import Person, Users


class UserService:
    @staticmethod
    async def get_user_profile(email: str):
        async with session_scope() as session:
            query = (
                select(
                    Users.email,
                    Person.name,
                    Person.DOB,
                    Person.sex,
                    Person.profile,
                    Person.phone_number,
                )
                .join_from(Users, Person)
                .where(Users.email == email)
            )
            return (await session.execute(query)).mappings().one()
