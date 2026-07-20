from sanic import Request, json, Blueprint
from app.models.models import User

from app.services.auth import protected
from app.services.profile import get_users_accounts

profile_bp = Blueprint('profile', url_prefix='/profile')


@profile_bp.route("/user_info", methods=['GET'])
@protected
async def users_info(request: Request) -> json:
    user = await request.ctx.session.get(User, request.ctx.user_id)
    return json(user.as_dict(), default=str)


@profile_bp.route("/user_accounts", methods=['GET'])
@protected
async def users_accounts(request: Request) -> json:
    accounts = await get_users_accounts(request.ctx.session, request.ctx.user_id)
    return json(accounts, default=str)
