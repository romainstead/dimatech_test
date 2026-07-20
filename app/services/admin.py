from functools import wraps

import jwt
from sanic import json
from sqlalchemy import select

from app.models.models import Admin


def admin_protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            token = request.token
            if not token:
                return json({"error": "Unauthorized"}, status=401)
            try:
                payload = jwt.decode(token, request.app.config.SECRET_KEY, algorithms=["HS256"])
            except jwt.exceptions.InvalidTokenError:
                return json({"error": "Invalid token"}, status=401)

            if payload.get("type") != "admin":
                return json({"error": "Forbidden"}, status=403)

            request.ctx.admin_login = payload["login"]
            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator(wrapped)


async def get_admin_by_email(request_session, email) -> Admin | None:
    query = select(Admin).filter_by(login=email)
    result = await request_session.execute(query)
    return result.scalars().first()
