import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str]
    password: Mapped[str]
    is_activated: Mapped[bool] = mapped_column(default=False)
    activation_link: Mapped[str]

    notes: Mapped[List["NoteModel"]] = relationship()

class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[Optional[str]]
    date: Mapped[str] = mapped_column(TIMESTAMP, default=datetime.datetime.now())

    user: Mapped["UserModel"] = relationship()

class TokenModel(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    refresh_token: Mapped[str]
