"""create test users and account

Revision ID: 0002_seed_test_data
Revises: 0001_create_tables
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, UTC
from passlib.context import CryptContext

revision = "8028be9ec449"
down_revision = "60284f3a0333"
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TEST_USER_LOGIN = "user@test.com"
TEST_USER_PASSWORD = "user12345"

TEST_ADMIN_LOGIN = "admin@test.com"
TEST_ADMIN_PASSWORD = "admin12345"


def upgrade() -> None:
    now = datetime.now(UTC)

    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("login", sa.String),
        sa.column("full_name", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    admins_table = sa.table(
        "admins",
        sa.column("id", sa.Integer),
        sa.column("login", sa.String),
        sa.column("full_name", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    accounts_table = sa.table(
        "accounts",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("amount", sa.Float),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    conn = op.get_bind()

    result = conn.execute(
        users_table.insert().values(
            login=TEST_USER_LOGIN,
            full_name="Test User",
            password_hash=pwd_context.hash(TEST_USER_PASSWORD),
            created_at=now,
            updated_at=now,
        ).returning(users_table.c.id)
    )
    user_id = result.scalar()

    conn.execute(
        accounts_table.insert().values(
            user_id=user_id,
            amount=0.0,
            created_at=now,
            updated_at=now,
        )
    )

    conn.execute(
        admins_table.insert().values(
            login=TEST_ADMIN_LOGIN,
            full_name="Test Admin",
            password_hash=pwd_context.hash(TEST_ADMIN_PASSWORD),
            created_at=now,
            updated_at=now,
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM accounts WHERE user_id IN (SELECT id FROM users WHERE login = :login)"
        ),
        {"login": TEST_USER_LOGIN},
    )
    conn.execute(sa.text("DELETE FROM users WHERE login = :login"), {"login": TEST_USER_LOGIN})
    conn.execute(sa.text("DELETE FROM admins WHERE login = :login"), {"login": TEST_ADMIN_LOGIN})