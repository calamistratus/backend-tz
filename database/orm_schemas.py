from datetime import datetime

from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column


class Base(DeclarativeBase):
    pass


class VeryUnimportantData(Base):
    """
    Access_levels: 0 to read, 3 to write
    """
    __tablename__ = 'very_unimportant_data'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String)

    __table_args__ = {
        'extend_existing': True
    }


class UnimportantData(Base):
    """
    Access_levels: 1 to read, 3 to write
    """
    __tablename__ = 'unimportant_data'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime)

    __table_args__ = {
        'extend_existing': True
    }


class ImportantData(Base):
    """
    Access_levels: 2 to read, 3 to write
    """
    __tablename__ = 'important_data'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime)
    amount: Mapped[int] = mapped_column(Integer)

    __table_args__ = {
        'extend_existing': True
    }


class Accounts(Base):
    """
    ORM class for processed account details.\n
    Contains id, username, hashed email and hashed password, encrypted name and email \n
    Access_levels: 4 to read, 5 to write
    """
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    access_level_enc: Mapped[str] = mapped_column(String)
    username_enc: Mapped[str] = mapped_column(String)
    email_enc: Mapped[str] = mapped_column(String)
    name_enc: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    email_hash: Mapped[str] = mapped_column(String, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean)

    __table_args__ = {
        'extend_existing': True
    }