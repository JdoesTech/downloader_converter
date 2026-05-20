import logging
import re
from typing import Optional, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import false

from app.model.person import Sex


T = TypeVar("T")

#get root logger
logger = logging.getLogger(__name__)

class RegisterSchema(BaseModel):
    
    fname: str
    lname: str
    email: str
    password: str
    phone_number: str
    birth: str
    sex: Sex
    profile: str = "base64"
    
    #phone number validation
    @field_validator
    def phone_validator(cls, v):
        logger.debug(f"Phone in 2 validator: {v}")
        
        #regex phone number
        regex = r"^[\+]?[(]?[0-9]{4}[)]?[-\s\.]?[0-9]{4}[-\s\.]?[0-9]{4,6}$"
        if v and not re.search(regex, v, re.I):
            raise HTTPException(status_code = 400, detail={"status": "Bad Request", "message": "Invalid Phone Number"})
        return v
    
    #Sex Validation
    @field_validator
    def sex_validator(cls, v):
        if hasattr(Sex, v) is False:
            raise HTTPException(status_code = 400, detail={"status": "Bad Request", "message": "Invalid Gender"})
        return v
    
    
class LoginSchema(BaseModel):
    email: str
    password: str
    
class ForgotPasswordSchema(BaseModel):
    email: str
    new_password: str
    
class DetailSchema(BaseModel):
    status: str
    message: str
    result: Optional[T] = None 
    
class ResponseSchema(BaseModel):
    detail: str
    result: Optional["T"] = None
    

    