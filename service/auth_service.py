import json
from datetime import datetime, timedelta, UTC

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from cache import redis_client
from exceptions import LoginException, LoginExpiredException, LoginInvalidException
from schemas import TokenDict, Account, LoginInfo
from service.conversions_service import process_account, generate_id
from settings import settings
from database import AccountsRepository


def give_jwt_token(token_dict: TokenDict) -> str:
    """
    Converts token dict to jwt token, used only for the registered users
    :param token_dict: TokenDict object
    :return: str - jwt token
    """
    return jwt.encode(
        payload={'id': token_dict.id,
                 'access_level': token_dict.access_level,
                 "exp": datetime.now(UTC) + timedelta(hours=24)},
        key=settings.jwt_secret,
        algorithm='HS256'
    )


async def create_temp_user(temp_id: str) -> int:
    """
    Essentially initializes temp_id in redis, creating temp user
    :param temp_id: Temporary user username
    :return: int - id of the user
    """
    r = redis_client
    if raw_used_ids := await r.get('used_ids_redis'):
        used_ids = json.loads(raw_used_ids)
        account_id = generate_id(used_ids=used_ids)
        used_ids.append(account_id)
        await r.set(
            temp_id,
            json.dumps({'id': account_id}),
            ex=60 * 60 * 24
        )
        await r.set(
            'used_ids_redis',
            json.dumps(used_ids),
            ex=60 * 60 * 24
        )
        settings.print(f'Temp user {temp_id} has been given id {account_id}')
        return account_id
    raise LoginException


async def get_token_dict(access_token: str = '', temp_id: str = '') -> TokenDict:
    """
    Input access_token to get registered user's token dict and temp id for temporary's
    :param access_token: Registered user access token (Default=None)
    :param temp_id: Temporary user username (Default=None)
    :return: TokenDict object
    """
    if access_token:  # Registered user login
        try:
            payload = jwt.decode(
                access_token,
                key=settings.jwt_secret,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise LoginExpiredException
        except jwt.InvalidTokenError:
            raise LoginInvalidException

        r = redis_client
        if used_ids_raw := await r.get('used_ids_postgres'):
            if payload.get('id') in set(json.loads(used_ids_raw)):
                settings.print(f'Registered user login successful {payload.get("id")}')
                return TokenDict(
                    id=payload.get('id'),
                    access_level=payload.get('access_level')
                )
        else:
            raise LoginException(message='The account seems to be deleted')

    elif temp_id:  # Temp user login
        r = redis_client
        if await r.get(temp_id) is None:
            account_id = await create_temp_user(temp_id)  # Give temp user a redis id if none
        else:
            account_id = json.loads(await r.get(temp_id))['id']  # Otherwise retrieve the id
            settings.print(f'Temp user login successful {account_id}')

        return TokenDict(
            id=account_id,
            access_level=0
        )
    raise LoginException(message='There was an error')

async def login(login_info: LoginInfo, session: AsyncSession) -> str:
    """
    Login account
    :param login_info: LoginInfo object
    :param session: AsyncSession object
    :return: str - jwt token
    """
    repo = AccountsRepository(session)
    token_dict = await repo.check_login(login_info)
    return give_jwt_token(token_dict)

async def register(account: Account, session: AsyncSession, access_level: int = 1) -> bool:
    """
    Register account
    :param access_level: int
    :param account: Account object
    :param session: AsyncSession object
    :return: bool - True if success
    """
    account_processed = await process_account(account, access_level=access_level)
    repo = AccountsRepository(session)
    await repo.create_account(account_processed)
    return True

async def delete(login_info: LoginInfo, session: AsyncSession, soft: bool) -> bool:
    """
    Delete account
    :param soft: Do not delete the account, but shut it off
    :param login_info: LoginInfo object
    :param session: AsyncSession object
    :return: bool - True if success
    """
    repo = AccountsRepository(session)
    return await repo.delete_account(login_info, soft)

async def update(account: Account, token_dict: TokenDict, session: AsyncSession) -> bool:
    """
    Updates Account in repository
    :param account: Account object
    :param token_dict: TokenDict object
    :param session: AsyncSession object
    :return: bool - True if success
    """
    repo = AccountsRepository(session)
    account_processed = await process_account(account=account, create_id=False)
    await repo.update_account(account=account, account_processed=account_processed, token_dict=token_dict)
    return True
