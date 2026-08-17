import logging
import re
from datetime import date, datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, EmailStr, field_validator

from app.model.person import Sex

T = TypeVar("T")
logger = logging.getLogger(__name__)


class RegisterSchema(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    password: str
    phone_number: str
    birth: str
    sex: Sex
    profile: str = ""

    @field_validator("phone_number")
    @classmethod
    def phone_validator(cls, value: str) -> str:
        regex = r"^[\+]?[(]?[0-9]{4}[)]?[-\s\.]?[0-9]{4}[-\s\.]?[0-9]{4,6}$"
        if value and not re.search(regex, value, re.I):
            raise ValueError("Invalid phone number")
        return value

    @field_validator("password")
    @classmethod
    def password_validator(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @field_validator("birth")
    @classmethod
    def birth_validator(cls, value: str) -> str:
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                datetime.strptime(value, fmt)
                return value
            except ValueError:
                continue
        raise ValueError("Birth date must use YYYY-MM-DD or DD-MM-YYYY format")


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_validator(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class DetailSchema(BaseModel):
    status: str
    message: str
    result: Optional[T] = None


class ResponseSchema(BaseModel):
    detail: str
    result: Optional[T] = None


def parse_birth(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Invalid birth date format")
