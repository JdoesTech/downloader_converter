from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_roles
from app.repository.auth_repo import JWTBearer
from app.schema import ResponseSchema
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["user"])


@router.post("/me", response_model=ResponseSchema, response_model_exclude_none=True)
async def get_user_profile(token: str = Depends(JWTBearer())):
    payload = get_current_user(token)
    result = await UserService.get_user_profile(payload["email"])
    return ResponseSchema(detail="Successfully fetched data", result=dict(result))


@router.get("/admin/ping", response_model=ResponseSchema, response_model_exclude_none=True)
async def admin_ping(payload: dict = Depends(require_roles("admin"))):
    return ResponseSchema(
        detail="Admin access granted",
        result={"email": payload["email"], "roles": payload.get("roles", [])},
    )
