import jwt
from datetime import datetime, timedelta
from decouple import config
from typing import Optional

from fastapi.requests import Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from starlette.exceptions import HTTPException

from db import database
from models import User

class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
            payload = {
                "sub": str(user.id),
                "exp": (
                    datetime.utcnow() + timedelta(minutes=int(config("TOKEN_LIFETIME")))
                ).replace(microsecond=0).timestamp()
            }
            return jwt.encode(
                payload=payload,
                key=config("SECRET_KEY"),
                algorithm=config("ALGORITHM")
            )
        except Exception as ex:
            raise ex


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    )-> Optional[HTTPBasicCredentials]:
        res = await super().__call__(request)

        try:
            payload = jwt.decode(
                jwt=res.credentials,
                key=config("SECRET_KEY"),
                algorithms=[config("ALGORITHM")]
            )
            user_data = await database.fetch_one(User.select().where(User.c.id == payload["sub"]))
            request.state.user = user_data
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")

oauth2_scheme = CustomHTTPBearer()
