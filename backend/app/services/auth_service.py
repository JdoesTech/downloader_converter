from uuid import uuid4

from fastapi import HTTPException
from passlib.context import CryptContext

from app.config import DEBUG
from app.model import Person, UserRole, Users
from app.model.role import Role
from app.repository.auth_repo import JWTRepo
from app.repository.person import PersonRepository
from app.repository.role import RoleRepository
from app.repository.user_role import UserRoleRepository
from app.repository.users import UsersRepository
from app.schema import (
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
    parse_birth,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_PROFILE_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)

INVALID_CREDENTIALS_MESSAGE = "Invalid email or password"
PASSWORD_RESET_MESSAGE = (
    "If an account exists for that email, password reset instructions have been sent."
)


class AuthService:
    @staticmethod
    async def register_service(register: RegisterSchema) -> None:
        existing_email = await UsersRepository.find_by_email(register.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        person_id = str(uuid4())
        user_id = str(uuid4())
        full_name = f"{register.fname} {register.lname}".strip()
        dob = parse_birth(register.birth)

        person = Person(
            id=person_id,
            name=full_name,
            DOB=dob,
            sex=register.sex,
            profile=register.profile or DEFAULT_PROFILE_IMAGE,
            phone_number=register.phone_number,
        )
        user = Users(
            id=user_id,
            fname=register.fname,
            lname=register.lname,
            email=register.email,
            password=pwd_context.hash(register.password),
            person_id=person_id,
        )

        role = await RoleRepository.find_by_role_name("user")
        if role is None:
            raise HTTPException(status_code=500, detail="Default user role is not configured")

        user_role = UserRole(user_id=user_id, role_id=role.id)

        await PersonRepository.create(**person.model_dump())
        await UsersRepository.create(**user.model_dump())
        await UserRoleRepository.create(**user_role.model_dump())

    @staticmethod
    async def logins_service(login: LoginSchema) -> str:
        user = await UsersRepository.find_by_email(login.email)
        if user is None or not pwd_context.verify(login.password, user.password):
            raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS_MESSAGE)

        roles = [role.role_name for role in user.roles]
        return JWTRepo(data={"sub": user.id, "email": user.email, "roles": roles}).generate_token()

    @staticmethod
    async def forgot_password_service(forgot_password: ForgotPasswordSchema) -> dict | None:
        user = await UsersRepository.find_by_email(forgot_password.email)
        if user is None:
            return None

        reset_token = JWTRepo.generate_reset_token(user.email)
        if DEBUG:
            return {"reset_token": reset_token}
        return None

    @staticmethod
    async def reset_password_service(reset_password: ResetPasswordSchema) -> None:
        email = JWTRepo.verify_reset_token(reset_password.token)
        user = await UsersRepository.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid reset token")

        await UsersRepository.update_password(
            email,
            pwd_context.hash(reset_password.new_password),
        )


async def generate_role() -> None:
    roles = await RoleRepository.find_by_role_names(["admin", "user"])
    if roles:
        return

    await RoleRepository.create_list(
        [
            Role(id=str(uuid4()), role_name="admin"),
            Role(id=str(uuid4()), role_name="user"),
        ]
    )
