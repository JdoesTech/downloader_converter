from typing import list, Optional
from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field, Relationship
from app.model.mixins import TimeMixin


class UserRole(SQLModel, TimeMixin, table=True):
    __tablename__="user_role"
    
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", primary_key=True)
    role_id: Optional[str] = Field(default=None, foreign_key="role.id", primary_key=True)