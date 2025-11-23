import hashlib
import json
from datetime import datetime

import bcrypt
from cryptography.fernet import Fernet
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from cache import redis_client
from database.orm_schemas import Accounts, VeryUnimportantData, ImportantData, UnimportantData, Base
from exceptions import EmailTakenException, InputException, AccessException
from schemas import AccountProcessed, Account, TokenDict, LoginInfo, UnimportantRow, ImportantRow, VeryUnimportantRow
from settings import settings


def check_access_level(method: str, access_level: int, access_levels: dict):
    if access_level < access_levels[method]:
        raise AccessException(needed_level=access_levels[method], current_level=access_level)


class AccountsRepository:
    access_levels = {'read': 4, 'write': 5}
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ids(self) -> list[int]:
        query = select(Accounts.id)
        result = await self.session.execute(query)
        ids = list(
            result.scalars().all()
        )

        return ids if ids else []

    async def update_redis(self, is_setup: bool = False) -> bool:
        ids = await self.get_ids()
        r = redis_client
        await r.set('used_ids_postgres', json.dumps(ids))

        if is_setup:
            await r.set('used_ids_redis', json.dumps([]))

        return True

    async def get_account_by_id(self, account_id: int) -> AccountProcessed:
        query = select(Accounts).where(Accounts.id == account_id)
        result = await self.session.execute(query)
        account_processed = AccountProcessed.model_validate(
            result.scalars().first()
        )

        return account_processed

    async def check_login(self, login_info: LoginInfo) -> TokenDict:
        email_hash = hashlib.sha256(login_info.email.lower().encode()).hexdigest()
        query = select(Accounts).where(Accounts.email_hash==email_hash)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(login_info.password.encode(), i.password_hash.encode()):
                f = Fernet(key=settings.access_level_secret)
                access_level = f.decrypt(i.access_level_enc.encode()).decode()
                settings.print(f'Login successful for :{i.id}')
                return TokenDict(
                    id=i.id,
                    access_level=int(access_level)
                )
        raise InputException(invalid_field='password')

    async def create_account(self, account: AccountProcessed) -> bool:
        query = select(1).where(Accounts.email_hash==account.email_hash).exists()  # Check for matching emails
        result = await self.session.scalar(select(query))
        if result:
            raise EmailTakenException()

        account_db = Accounts(
            is_active=account.is_active,
            email_hash=account.email_hash,
            password_hash=account.password_hash,
            email_enc=account.email_enc,
            name_enc=account.name_enc,
            username_enc=account.username_enc,
            access_level_enc=account.access_level_enc,
            id=account.id
        )
        self.session.add(account_db)
        await self.session.commit()
        await self.update_redis()
        settings.print(f'Created account {account.id}')
        return True

    async def update_account(self, account: Account, account_processed: AccountProcessed, token_dict: TokenDict) -> bool:
        query = select(Accounts).where(Accounts.id==token_dict.id)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(account.password.encode(), i.password_hash.encode()):
                i.username_enc=account_processed.username_enc
                i.name_enc=account_processed.name_enc
                i.email_enc=account_processed.email_enc
                i.email_hash=account_processed.email_hash

                await self.session.commit()
                settings.print(f'Updated account, id:{i.id}')
                return True
        return False

    async def delete_account(self, login_info: LoginInfo, soft: bool) -> bool:
        email_hash = hashlib.sha256(login_info.email.lower().encode()).hexdigest()
        query = select(Accounts).where(Accounts.email_hash==email_hash)
        result = await self.session.execute(query)
        for i in result.scalars().all():
            if bcrypt.checkpw(login_info.password.encode(), i.password_hash.encode()):
                if soft:
                    i.is_active=False
                else:
                    query = delete(Accounts).where(Accounts.id==i.id)
                    await self.session.execute(query)
                await self.session.commit()
                settings.print(f'Deleted account, id:{i.id}, soft={soft}')
                return True
        return False

    async def get_all(self, access_level: int = 5) -> list[AccountProcessed]:
        check_access_level('read', access_level, self.access_levels)
        query = select(Accounts)
        result = await self.session.execute(query)
        result = list(result.scalars().all())
        return [AccountProcessed.model_validate(i) for i in result]

# I know that they have the same functions, but I've decided not to work on that because it's all mockdata
class VeryUnimportantDataRepository:
    access_levels = {'read':0, 'write':3}
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, access_level: int = 5) -> list[VeryUnimportantRow]:
        check_access_level('read', access_level, self.access_levels)
        query = select(VeryUnimportantData)
        result = await self.session.execute(query)
        result = list(result.scalars().all())
        return [VeryUnimportantRow.model_validate(i) for i in result]

    async def add_all(self, objects: list[VeryUnimportantData]) -> bool:
        self.session.add_all(objects)
        await self.session.commit()
        return True


class UnimportantDataRepository:
    access_levels = {'read': 1, 'write': 3}
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, access_level: int = 5) -> list[UnimportantRow]:
        check_access_level('read', access_level, self.access_levels)
        query = select(UnimportantData)
        result = await self.session.execute(query)
        result = list(result.scalars().all())
        return [UnimportantRow.model_validate(i) for i in result]

    async def add_all(self, objects: list[UnimportantData]) -> bool:
        self.session.add_all(objects)
        await self.session.commit()
        return True


class ImportantDataRepository:
    access_levels = {'read': 2, 'write': 3}
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, access_level: int = 5) -> list[ImportantRow]:
        check_access_level('read', access_level, self.access_levels)
        query = select(ImportantData)
        result = await self.session.execute(query)
        result = list(result.scalars().all())
        return [ImportantRow.model_validate(i) for i in result]

    async def add_all(self, objects: list[ImportantData]) -> bool:
        self.session.add_all(objects)
        await self.session.commit()
        return True

poem = """There will come soft rains and the smell of the ground
And swallows circling with their shimmering sound
And frogs in the pools singing at night
And wild plum-trees in tremulous white
Robins will wear their feathery fire
Whistling their whims on a low fence-wire
And not one will know of the war, not one
Will care at last when it is done
Not one would mind, neither bird nor tree
If mankind perished utterly
And Spring herself, when she woke at dawn
Would scarcely know that we were gone""".split('\n')  # By Sara Teasdale, 1918

async def create_mock_data(session: AsyncSession):
    very_unimportant_data = []
    unimportant_data = []
    important_data = []
    for i in range(len(poem)):
        very_unimportant_data.append(VeryUnimportantData(
            id = i,
            text=poem[i],
        ))
        unimportant_data.append(UnimportantData(
            id = i,
            text = poem[i],
            date = datetime.now()
        ))
        important_data.append(ImportantData(
            id = i,
            text = poem[i],
            date = datetime.now(),
            amount = len(poem[i])
        ))
    repos = [VeryUnimportantDataRepository(session),
             UnimportantDataRepository(session),
             ImportantDataRepository(session)]
    datas =  [very_unimportant_data,
              unimportant_data,
              important_data]
    for repo, objects in zip(repos, datas):
        if await repo.get_all() == []:
          await repo.add_all(objects)