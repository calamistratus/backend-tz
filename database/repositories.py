import json

import bcrypt
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from cache import redis_client
from database.orm_schemas import Accounts
from schemas import AccountProcessed, Account


class AccountsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ids(self) -> list[int]:
        query = select(Accounts.id)
        result = await self.session.execute(query)
        ids = list(
            result.scalars().all()
        )

        return ids if ids else []

    async def update_redis(self) -> bool:
        ids = await self.get_ids()
        r = redis_client
        await r.set('used_ids', json.dumps(ids))

        return True

    async def get_account_by_id(self, account_id: int) -> AccountProcessed:
        query = select(Accounts).where(Accounts.id == account_id)
        result = await self.session.execute(query)
        account_processed = AccountProcessed.model_validate(
            result.scalars().first()
        )

        return account_processed

    async def check_login(self, account: Account) -> int:
        query = select(Accounts).where(Accounts.username==account.username)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(account.password.encode(), i.password_hash.encode()):
                print(f'Login successful for {i.username}, id:{i.id}')
                return i.id
        else:
            return 0

    async def create_account(self, account: AccountProcessed) -> bool:
        account_db = Accounts(
            email_hash=account.email_hash,
            password_hash=account.password_hash,
            email_enc=account.email_enc,
            name_enc=account.name_enc,
            username=account.username,
            id=account.id
        )
        self.session.add(account_db)
        await self.session.commit()
        return True

    async def update_account(self, account: AccountProcessed, new_password_hash:str) -> bool:
        query = select(Accounts).where(Accounts.username==account.username)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(account.password.encode(), i.password_hash.encode()):
                i.username=account.username
                i.name_enc=account.name_enc
                i.password_hash=new_password_hash
                i.email_enc=account.email_enc
                i.email_hash=account.email_hash

                await self.session.commit()
                print(f'Updated account {i.username}, id:{i.id}')
                return True
        return False

    async def delete_account(self, account: Account) -> bool:
        query = select(Accounts).where(Accounts.username==account.username)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(account.password.encode(), i.password_hash.encode()):
                query = delete(Accounts).where(Accounts.id==i.id)
                await self.session.execute(query)
                await self.session.commit()
                print(f'Deleted account {i.username}, id:{i.id}')
                return True
        return False
