from fastapi import Depends, HTTPException

from app.repository.auth_repo import JWTBearer, JWTRepo


def get_current_user(token: str) -> dict:
    payload = JWTRepo.extract_token(token)
    if not payload.get("email"):
        raise HTTPException(
            status_code=401,
            detail={"status": "Unauthorized", "message": "Invalid token payload."},
        )
    return payload


def require_roles(*allowed_roles: str):
    async def role_checker(token: str = Depends(JWTBearer())) -> dict:
        payload = get_current_user(token)
        user_roles = payload.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=403,
                detail={"status": "Forbidden", "message": "Insufficient permissions."},
            )
        return payload

    return role_checker
