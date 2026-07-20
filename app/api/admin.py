import jwt
from sanic import json, Blueprint, Request
from sqlalchemy import select, func, delete

from app.models.models import User, Admin, Account
from app.services.admin import admin_protected, get_admin_by_email
from app.services.auth import verify_password, get_hashed_password

admin_bp = Blueprint("admin", url_prefix="/admin")


@admin_bp.route("/create_admin", methods=["POST"])
@admin_protected
async def create_admin(request: Request):
    email = request.json['email']
    password = request.json['password']
    full_name = request.json['full_name']

    hashed_password = get_hashed_password(password)
    new_admin = Admin(login=email, password_hash=hashed_password, full_name=full_name)

    request.ctx.session.add(new_admin)
    await request.ctx.session.commit()

    return json(new_admin.as_dict())


@admin_bp.route("/login", methods=["POST"])
async def do_admin_login(request):
    email = request.json["email"]
    password = request.json["password"]

    user = await get_admin_by_email(request.ctx.session, email)
    if not user or not verify_password(password, user.password_hash):
        return json({"error": "Invalid credentials"}, status=401)

    token = jwt.encode(
        {"login": user.login, "type": "admin"},
        request.app.config.SECRET_KEY,
        algorithm="HS256",
    )
    return json({"access_token": token})


@admin_bp.route("/list_users/<page:int>", methods=["GET"])
@admin_protected
async def list_users(request, page):
    # пагинация
    limit = int(request.args.get("limit", 10))
    count_query = select(func.count()).select_from(User)
    total_result = await request.ctx.session.execute(count_query)
    total = total_result.scalar()
    offset = (page - 1) * limit

    query = select(User).offset(offset).limit(limit)
    result = await request.ctx.session.execute(query)
    users = result.scalars().all()
    total_pages = (total + limit - 1) // limit

    return json({
        "users": [u.as_dict() for u in users],
        "total": total,
        "total_pages": total_pages,
        "page": page
    }, default=str)


@admin_bp.route("/create_user", methods=["POST"])
@admin_protected
async def create_user(request: Request):
    email = request.json['email']
    password = request.json['password']
    full_name = request.json['full_name']

    hashed_password = get_hashed_password(password)
    new_user = User(login=email, password_hash=hashed_password, full_name=full_name)
    new_account = Account(user=new_user)

    request.ctx.session.add(new_account)
    request.ctx.session.add(new_user)
    await request.ctx.session.commit()

    return json(new_user.as_dict())


@admin_bp.route("/delete_user/<id:int>", methods=["DELETE"])
@admin_protected
async def delete_user(request: Request, id: int):
    query = delete(User).where(User.id == id)
    result = await request.ctx.session.execute(query)
    if result.rowcount == 0:
        return json({"error": "User not found"}, status=404)
    await request.ctx.session.commit()
    return json({"message": f"User with id={id} deleted succesfully"})


@admin_bp.route("/update_user/<id:int>", methods=["PATCH"])
@admin_protected
async def update_user_info(request, id):
    data = request.json
    allowed_fields = {"full_name", "login"}

    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    if not update_data:
        return json({"error": "No valid fields to update"}, status=400)

    if "login" in update_data:
        existing = await request.ctx.session.execute(
            select(User).where(User.login == update_data["login"], User.id != id)
        )
        if existing.scalar_one_or_none():
            return json({"error": "Login already taken"}, status=409)

    user = await request.ctx.session.get(User, id)
    if not user:
        return json({"error": "User not found"}, status=404)

    for key, value in update_data.items():
        setattr(user, key, value)

    await request.ctx.session.commit()
    return json(user.as_dict(), default=str)


@admin_bp.route("/update_user_password/<id:int>", methods=["PATCH"])
@admin_protected
async def update_user_password(request, id):
    new_password = request.json['new_password']
    user = await request.ctx.session.get(User, id)
    if not user:
        return json({"error": "User not found"}, status=404)
    hashed_password = get_hashed_password(new_password)
    setattr(user, "password_hash", hashed_password)
    await request.ctx.session.commit()
    return json(user.as_dict(), default=str)


@admin_bp.route("/get_user_accounts/<id:int>", methods=["GET"])
@admin_protected
async def get_user_accounts(request, id):
    user = await request.ctx.session.get(User, id)
    if not user:
        return json({"error": "User not found"}, status=404)
    result = await request.ctx.session.execute(select(Account).where(Account.user_id == id))
    accounts = result.scalars().all()
    return json({"user": user.as_dict(), "accounts": [a.as_dict() for a in accounts]}, default=str)