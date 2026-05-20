from sqlalchemy.future import select
from app.model import Users, Person
from app.config import db

class UserService:
    @staticmethod
    async def get_user_profile(email:str):
        query = select(Users.email, Person.name, Person.DOB, Person.sex, Person.profile, Person.phone_number).join_from(Users, Person).where(Users.email == email)
        return(await db.execute(query)).mappings().one()