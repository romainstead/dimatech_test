import os
import bcrypt
from functools import wraps
import jwt
from sanic import Request
from sanic.response import text
from sqlalchemy import select

from app.models.models import User

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'


def check_token(request: Request):
    if not request.token:
        return False
    try:
        payload = jwt.decode(
            request.token, request.app.config.SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        request.ctx.user_id = payload.get("user_id")
        return True


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if check_token(request):
                return await f(request, *args, **kwargs)
            return text("You are unauthorized.", 401)

        return decorated_function

    return decorator(wrapped)


def get_hashed_password(plain_text_password: str):
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt=bcrypt.gensalt())
    return hashed.decode('utf-8')


async def get_user_by_email(request_session, email) -> User | None:
    query = select(User).filter_by(login=email)
    result = await request_session.execute(query)
    return result.scalars().first()


def verify_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))
