from sqlalchemy import select, text

from app.models.models import Account


async def get_or_create_account(session, user_id: int, account_id: int) -> Account:
    result = await session.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if account is None:
        account = Account(id=account_id, user_id=user_id, amount=0.0)
        session.add(account)
        await session.flush()

        await session.execute(
            text("SELECT setval('accounts_id_seq', (SELECT MAX(id) FROM accounts))")
        )

    return account
