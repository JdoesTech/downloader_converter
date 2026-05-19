from datetime import datetime
from pydantic import BaseModel,Field
from sqlalchemy import Column, DateTime
from sqlmodel import Field

class TimeMixin:
    """Mixin validates the datetime value of when  an entity is created and last modified"""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    modified_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
