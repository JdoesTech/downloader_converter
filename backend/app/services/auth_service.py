import base64
import datetime
from uuid import uuid4
from fastapi import HTTPException
from passlib.context import CryptContext

from app.schema import ForgotPasswordSchema, LoginSchema, RegisterSchema
from app.model import Person, Users, UserRole
from app.repository.role import RoleRepository
from app.repository.users import UsersRepository
from app.repository.person import PersonRepository
from app.repository.user_role import UserRoleRepository
from app.repository.auth_repo import JWTRepo
from app.model.role import Role

#Encrypt Password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    async def register_service(register: RegisterSchema):
        #create uuid
        _person_id = str(uuid4())
        _users_id = str(uuid4())
        
        # convert birth date type from frontend str to date
        birth_date = datetime.strftime(register.birth, "%d-%m-$Y")
        
        #open image profile default to string base64
        with open("./media/profile.png", "rb") as f:
            image_str = base64.b64decode(f.read())
        image_str = "data:image/png;base64,"+ image_str.decode("utf-8")
        
        # mapping request data to class entity table
        _person = Person(id=_person_id, 
                        fname=register.fname, 
                        lname=register.lname, 
                        birth=register.birth, 
                        sex=register.sex, 
                        profile=image_str, 
                        phone_number=register.phone_number)
        
        _users = Users(id=_users_id, 
                    fname=register.fname, 
                    lname=register.lname, 
                    email=register.email, 
                    password=pwd_context(register.password), 
                    person_id=_person_id)
        
        _role = await RoleRepository.find_by_role_name("user")
        _users_role = UserRole(users_id= _users_id, role_id=_role.id)
        
        #checking the same email
        _email = await UsersRepository.find_by_email(register.email)
        if _email: 
            raise HTTPException(status_code=400, detail="Email already exists!")
        else:
            #insert to tables
            await PersonRepository.create(**_person.model_dump())
            await UsersRepository.create(**_users.model_dump())
            await UserRoleRepository.create(**_users_role.model_dump())
            
    @staticmethod
    async def logins_service(login: LoginSchema):
        _email = await UsersRepository.find_by_email(login.email)
        if _email is not None:
            if not pwd_context.verify(login.password,_email.password):
                raise HTTPException(status_code=400, detail= "Invalid Password")
            return JWTRepo(data={"email": _email.email}).generate_token()
        raise HTTPException(status_code=404, detail= "Email not found")
    
    @staticmethod
    async def forgot_password_service(forgot_password: ForgotPasswordSchema):
        _email = await UsersRepository.find_by_email(forgot_password.email)
        if _email is None:
            raise HTTPException(status_code=400, detail= "Email not Found")
        await UsersRepository.update_password(forgot_password.email, pwd_context(forgot_password.new_password))
        
        
#Generate roles manually
async def generate_role():
    _role = await RoleRepository.find_by_list_role(["admin", "user"])
    if not _role:
        await RoleRepository.create_list([Role(id=str(uuid4()), role_name="admin"), Role(id=str(uuid4()), role_name="user")])
        