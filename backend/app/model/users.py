from typing import Optional, List
from sqlalchemy import Column, String, table
from sqlmodel import SQLModel, Field, Relationship

from app.model.mixins import TimeMixin
from app.model.user_role import UserRole


class Users(SQLModel, TimeMixin, table=True):
    __tablename__="users"
    
    id: Optional[str]= Field(None, primary_key=True, nullable=False)
    fname: str =Field(sa_column=Column("firstName", String, unique=False))
    lname: str =Field(sa_column=Column("lastName", String, unique=False))
    email: str =Field(sa_column=Column("email", String, unique=True))
    password: str
    
    person_id: Optional[str] = Field(default=None, foreign_key="person.id")
    person: Optional["Person"] = Relationship(back_populates="users")
    
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)