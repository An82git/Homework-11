from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Date, DateTime, ForeignKey

class Base(DeclarativeBase):
    pass

class Contacts(Base):
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement="auto")
    name: Mapped[str]
    surname: Mapped[str]
    email_address: Mapped[str]
    phone_number: Mapped[str]
    birthday = mapped_column(Date)
    additional_data: Mapped[str] = mapped_column(nullable=True)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement="auto")
    username: Mapped[str]
    email: Mapped[str]
    phone_number: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str]
    avatar: Mapped[str] = mapped_column(nullable=True)
    created_at = mapped_column(DateTime)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    confirmed: Mapped[bool] = mapped_column(default=False)
