from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column


class Base(DeclarativeBase):
    pass


class Accounts(Base):
    """
    ORM class for processed account details.\n
    Contains id, username, hashed email and hashed password, encrypted name and email
    """
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] #= mapped_column(primary_key=True) In case you want unique usernames
    email_enc: Mapped[str]
    name_enc: Mapped[str]
    password_hash: Mapped[str]
    email_hash: Mapped[str] = mapped_column(unique=True)

    __table_args__ = {
        "extend_existing": True
    }