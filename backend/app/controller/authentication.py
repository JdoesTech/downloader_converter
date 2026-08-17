from uuid import uuid4

from fastapi import APIRouter, Depends

from app.dependencies.rate_limit import auth_rate_limit
from app.schema import (
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
    ResponseSchema,
)
from app.services.auth_service import PASSWORD_RESET_MESSAGE, AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ResponseSchema, response_model_exclude_none=True)
async def register(
    request_body: RegisterSchema,
    _: None = Depends(auth_rate_limit),
):
    await AuthService.register_service(request_body)
    return ResponseSchema(detail="Successfully registered")


@router.post("/login", response_model=ResponseSchema)
async def login(
    request_body: LoginSchema,
    _: None = Depends(auth_rate_limit),
):
    token = await AuthService.logins_service(request_body)
    return ResponseSchema(
        detail="Successfully login",
        result={"token_type": "Bearer", "access_token": token},
    )


@router.post("/forgot-password", response_model=ResponseSchema, response_model_exclude_none=True)
async def forgot_password(
    request_body: ForgotPasswordSchema,
    _: None = Depends(auth_rate_limit),
):
    debug_payload = await AuthService.forgot_password_service(request_body)
    response = ResponseSchema(detail=PASSWORD_RESET_MESSAGE)
    if debug_payload:
        response.result = debug_payload
    return response


@router.post("/reset-password", response_model=ResponseSchema, response_model_exclude_none=True)
async def reset_password(
    request_body: ResetPasswordSchema,
    _: None = Depends(auth_rate_limit),
):
    await AuthService.reset_password_service(request_body)
    return ResponseSchema(detail="Password updated successfully")
