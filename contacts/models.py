from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Date

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
