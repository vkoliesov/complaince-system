from fastapi.exceptions import HTTPException

from passlib.context import CryptContext
from asyncpg import UniqueViolationError

from db import database
from managers.auth import AuthManager
from models import User, RoleType


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = User.metadata.tables.get("users")


class UserManager:
    @staticmethod
    async def register(user_data):
        user_data["password"] = pwd_context.hash(user_data["password"])
        try:
            id_ = await database.execute(users.insert().values(**user_data))
        except UniqueViolationError:
            raise HTTPException(400, "User with this email already exists")
        user_do = await database.fetch_one(users.select().where(users.c.id == id_))
        return AuthManager.encode_token(user_do)

    @staticmethod
    async def login(user_data):
        user_do = await database.fetch_one(
            users.select().where(users.c.email == user_data["email"])
        )
        if not user_do:
            raise HTTPException(400, "Wrong email or password")
        elif not pwd_context.verify(user_data["password"], user_do["password"]):
            raise HTTPException(400, "Wrong email or password")

        return AuthManager().encode_token(user_do)

    @staticmethod
    async def get_all_users():
        return await database.fetch_all(users.select())

    @staticmethod
    async def get_user_by_email(email):
        return await database.fetch_one(users.select().where(users.c.email == email))

    @staticmethod
    async def change_role(role: RoleType, user_id: int):
        return await database.execute(
            users.update().where(users.c.id == user_id).values(role=role)
        )
