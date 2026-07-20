from datetime import datetime, UTC, timedelta

from sanic import json, Blueprint
from app.services.auth import get_user_by_email, verify_password
import jwt

login_bp = Blueprint("login", url_prefix="/login")


@login_bp.route("/", methods=["POST"])
async def do_login(request):
    email = request.json["email"]
    password = request.json["password"]

    user = await get_user_by_email(request.ctx.session, email)
    if not user or not verify_password(password, user.password_hash):
        return json({"error": "Invalid credentials"}, status=401)

    token = jwt.encode(
        {"user_id": user.id, "type": "user", "exp": datetime.now(UTC) + timedelta(hours=24)},
        request.app.config.SECRET_KEY,
        algorithm="HS256",
    )
    return json({"access_token": token})
