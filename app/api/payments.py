import hashlib
import hmac

from sanic import json, Blueprint
from sqlalchemy import select

from app.models.models import Payment
from app.services.payments import get_or_create_account

payment_bp = Blueprint("payments", url_prefix="/payments")


@payment_bp.route("/make_transaction", methods=["POST"])
async def payment_webhook(request):
    data = request.json

    expected_signature = hashlib.sha256(f"{data['account_id']}"
                                        f"{data['amount']}"
                                        f"{data['transaction_id']}"
                                        f"{data['user_id']}{request.app.config.SECRET_KEY}".encode()).hexdigest()
    if not hmac.compare_digest(data["signature"], expected_signature):
        return json({"error": "Invalid signature"}, status=400)

    existing = await request.ctx.session.execute(
        select(Payment).where(Payment.transaction_id == data["transaction_id"])
    )
    if existing.scalar_one_or_none():
        return json({"message": "Transaction already processed"}, status=200)

    account = await get_or_create_account(request.ctx.session, user_id=data["user_id"], account_id=data["account_id"])
    new_payment = Payment(account_id=account.id,
                          amount=data["amount"],
                          transaction_id=data["transaction_id"],
                          user_id=data["user_id"])
    request.ctx.session.add(new_payment)
    setattr(account, "amount", account.amount + data["amount"])
    await request.ctx.session.commit()
    return json({"message": "Payment successfully created"}, status=201)
