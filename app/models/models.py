from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, int_pk, str_uniq


class User(Base):
    id: Mapped[int_pk]
    login: Mapped[str_uniq] = mapped_column(String(50), unique=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str_uniq] = mapped_column(String(255), nullable=False)
    accounts: Mapped[list["Account"]] = relationship(back_populates="user")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")

    def as_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "full_name": self.full_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Admin(Base):
    id: Mapped[int_pk]
    login: Mapped[str_uniq] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "full_name": self.full_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Account(Base):
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column((ForeignKey('users.id', ondelete="CASCADE")), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(back_populates="account")

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Payment(Base):
    id: Mapped[int_pk]
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="payments")
    account: Mapped["Account"] = relationship(back_populates="payments")
