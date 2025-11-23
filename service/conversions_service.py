import json
from random import randint

import bcrypt
import hashlib
from cryptography.fernet import Fernet

from settings import settings
from cache import redis_client
from schemas import Account, AccountProcessed, LoginInfo


def generate_id(used_ids) -> int:
    """
    Generates a unique id, that's not in used_ids
    :param used_ids:
    :return: int - unique id from 1 to 9223372036854775806 inclusive
    """
    while (account_id := randint(1, 1111111)) in used_ids:
        pass
    return account_id

async def process_account(account: Account,
                          access_level: int = 1,
                          create_id: bool = True) -> AccountProcessed:
    """
    Convert an Account into an AccountProcessed
    :param access_level: int
    :param account: Account object
    :param create_id: Turn it off if you do not want to give processed account a unique id (Default=True)
    :return: AccountProcessed object
    """
    r = redis_client
    used_ids = set(json.loads(await r.get('used_ids')))

    if create_id:
        account_id = generate_id(used_ids)
    else:
        account_id = 0

    f = Fernet(key=settings.name_secret)
    name_enc = f.encrypt((account.name+' '+account.surname).title().encode()).decode()

    f = Fernet(key=settings.email_secret)
    email_enc = f.encrypt(account.email.encode()).decode()

    f = Fernet(key=settings.access_level_secret)
    access_level_enc = f.encrypt(str(access_level).encode()).decode()

    f = Fernet(key=settings.username_secret)
    username_enc = f.encrypt(account.username.encode()).decode()

    password_hash = bcrypt.hashpw(account.password.encode(), bcrypt.gensalt()).decode()
    email_hash = hashlib.sha256(account.email.lower().encode()).hexdigest()

    return AccountProcessed(
        id=account_id,
        access_level_enc=access_level_enc,
        username_enc=username_enc,
        name_enc=name_enc,
        email_enc=email_enc,
        email_hash=email_hash,
        password_hash=password_hash,
        is_active=True
    )

def unprocess_account(account_processed: AccountProcessed) -> Account:
    """
    Converts AccountProcessed into Account, gives blank password
    :param account_processed: AccountProcessed object
    :return: Account object
    """
    f = Fernet(key=settings.email_secret)
    email = f.decrypt(account_processed.email_enc.encode()).decode()

    f = Fernet(key=settings.name_secret)
    full_name = f.decrypt(account_processed.name_enc.encode()).decode().split()

    f = Fernet(key=settings.username_secret)
    username = f.decrypt(account_processed.username_enc.encode()).decode()

    return Account(
        username=username,
        name = full_name[0],
        surname = full_name[1],
        password='',
        email=email
    )

def account_to_login_info(account: Account) -> LoginInfo:
    """
    Converts Account object to LoginInfo object
    :param account: Account object
    :return: LoginInfo object
    """
    return LoginInfo(
        email=account.email,
        password=account.password
    )