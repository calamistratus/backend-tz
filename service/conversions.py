import json
from random import randint

import bcrypt
import hashlib
from cryptography.fernet import Fernet

from settings import settings
from cache import redis_client
from schemas import Account, AccountProcessed

async def process_account(account: Account, create_id=True) -> AccountProcessed:
    r = redis_client
    used_ids = set(json.loads(await r.get('used_ids')))

    if create_id:
        while (account_id := randint(1, 9223372036854775806)) in used_ids:
            pass
    else:
        account_id = 0

    f = Fernet(key=settings.name_secret)
    name_enc = f.encrypt((account.name+' '+account.surname).title().encode()).decode()

    f = Fernet(key=settings.email_secret)
    email_enc = f.encrypt(account.email.encode()).decode()

    password_hash = bcrypt.hashpw(account.password.encode(), bcrypt.gensalt()).decode()
    email_hash = hashlib.sha256(account.email.lower().encode()).hexdigest()

    return AccountProcessed(
        id=account_id,
        username=account.username,
        name_enc=name_enc,
        email_enc=email_enc,
        email_hash=email_hash,
        password_hash=password_hash
    )

async def unprocess_account(account_processed: AccountProcessed) -> Account:
    f = Fernet(key=settings.email_secret)
    email = f.decrypt(account_processed.email_enc.encode()).decode()

    f = Fernet(key=settings.name_secret)
    full_name = f.decrypt(account_processed.name_enc.encode()).decode().split()

    return Account(
        name = full_name[0],
        surname = full_name[1],
        password='',
        email=email
    )
