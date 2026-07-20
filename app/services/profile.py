from sqlalchemy import select
from app.models.models import Account


async def get_users_accounts(session, user_id: int):
    query = select(Account).filter_by(user_id=user_id)
    result = await session.execute(query)
    return [a.as_dict() for a in result.scalars().all()]
