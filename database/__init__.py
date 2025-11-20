from database.orm_schemas import Accounts
from database.database_getter import get_db_session, get_db_session_cm
from database.repositories import AccountsRepository

__all__ = ['Accounts', 'get_db_session', 'get_db_session_cm', 'AccountsRepository']

"""
CREATE TABLE accounts (
	id BIGINT PRIMARY KEY,
	name_enc VARCHAR,
	email_enc VARCHAR UNIQUE NOT NULL,
	username VARCHAR,
	password_hash VARCHAR,
	email_hash VARCHAR
)
"""