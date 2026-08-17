from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, RESET_TOKEN_EXPIRE_MINUTES, SECRET_KEY


class JWTRepo:
    def __init__(self, data: dict | None = None) -> None:
        self.data = data or {}

    def generate_token(self, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = self.data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def generate_reset_token(email: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        payload = {"email": email, "purpose": "password_reset", "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def extract_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            raise HTTPException(
                status_code=401,
                detail={"status": "Unauthorized", "message": "Invalid or expired token."},
            ) from exc

    @staticmethod
    def verify_jwt(jwt_token: str) -> bool:
        try:
            jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except JWTError:
            return False

    @staticmethod
    def verify_reset_token(token: str) -> str:
        payload = JWTRepo.extract_token(token)
        if payload.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=400,
                detail={"status": "Bad Request", "message": "Invalid reset token."},
            )
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=400,
                detail={"status": "Bad Request", "message": "Invalid reset token."},
            )
        return email


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials is None:
            raise HTTPException(
                status_code=403,
                detail={"status": "Forbidden", "message": "Invalid authorization code."},
            )
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=403,
                detail={"status": "Forbidden", "message": "Invalid authentication schema."},
            )
        if not JWTRepo.verify_jwt(credentials.credentials):
            raise HTTPException(
                status_code=403,
                detail={"status": "Forbidden", "message": "Invalid token or expired token."},
            )
        return credentials.credentials
