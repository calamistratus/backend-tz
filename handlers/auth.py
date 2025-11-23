import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session, AccountsRepository
from exceptions import AccessException, InputException
from schemas import TokenDict, Account, LoginInfo, AdminCreatedAccount
from service import login, unprocess_account,  get_token_dict, register, delete, update, account_to_login_info, get_account
from settings import settings


router = APIRouter(prefix='/auth', tags=['auth'])
frontend = Jinja2Templates(directory='frontend')

@router.get("/")
async def index_auth(request: Request,
                     session: AsyncSession = Depends(get_db_session)) -> Response:
    response = frontend.TemplateResponse(
        'auth.html',
        {'request': request}
    )
    token_dict = await check_login_cookies(response=response, request=request)
    if token_dict.access_level:
        account = await AccountsRepository(session).get_account_by_id(token_dict.id)
        account = unprocess_account(account)
        print('Hello', account.name)
    else:
        print(f'Hello, temp user {token_dict.id}')

    return response


async def check_login_cookies(request: Request, response: Response = None) -> TokenDict:
    if access_token := request.cookies.get('access_token'):
        return await get_token_dict(access_token=access_token)
    elif temp_id := request.cookies.get('temp_id'):
        return await get_token_dict(temp_id=temp_id)
    else:
        temp_id = str(uuid.uuid4())
        response.set_cookie(
            key='temp_id',
            value=temp_id,
            max_age=60 * 60 * 24,
            samesite='lax'
        )
        settings.print(f'Created temp user {temp_id}')
        return await get_token_dict(temp_id=temp_id)


@router.post('/register')
async def register_user(account: Account,
                        session: AsyncSession = Depends(get_db_session)) -> RedirectResponse:
    if len(account.password) < 8:
        raise InputException(invalid_field='Password is too short, needs at least 8 characters')
    if len(account.username) < 3:
        raise InputException(invalid_field='Username is too short, needs at least 3 characters')
    if len(account.email) < 6 or not '@' in account.email or not '.' in account.email:
        raise InputException(invalid_field='Enter valid email address')

    await register(account, session)
    settings.print(f'Registered user {account.username}')
    return await login_user(
        login_info=account_to_login_info(account),
        session=session
    )


@router.post('/login')
async def login_user(login_info: LoginInfo,
                     session: AsyncSession = Depends(get_db_session)) -> RedirectResponse:
    jwt = await login(login_info, session)
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(
        key='access_token',
        value=jwt,
        max_age=60 * 60 * 24 * 3,
        samesite='lax'
    )
    settings.print(f'Login-ed user')
    return response


@router.post('/logout')
async def logout_user(request: Request) -> RedirectResponse:
        response = RedirectResponse(url='/', status_code=303)
        response.delete_cookie(key='access_token')
        return response

@router.post('/delete')
async def delete_user(login_info: LoginInfo,
                      session: AsyncSession = Depends(get_db_session)) -> RedirectResponse:
    await delete(login_info, session, soft=True)
    return await logout_user()

@router.post('/update')
async def update_user(account: Account, request: Request,
                      session: AsyncSession = Depends(get_db_session)) -> RedirectResponse:
    response = RedirectResponse(url='/', status_code=303)
    token_dict = await check_login_cookies(request, response)
    if token_dict.access_level > 0:
        await update(
            account=account,
            session=session,
            token_dict=token_dict
        )
        await logout_user()
        return await login_user(
            login_info=account_to_login_info(account),
            session=session
        )
    raise AccessException(needed_level=1, current_level=token_dict.access_level)

@router.get('/get_name')
async def get_user_name(request: Request,
                        session: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    token_dict = await check_login_cookies(request=request)
    if token_dict.access_level > 0:
        account = await get_account(account_id=token_dict.id, session=session)
        message = account.name
    else:
        message = 'Temp user'
    return JSONResponse(status_code=200, content={'name': message})

@router.post('/admin_create')
async def admin_create_account(request: Request,
                               account: AdminCreatedAccount,
                               session: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    token_dict = await check_login_cookies(request=request)
    if token_dict.access_level >= 4:
        await register(account=account.account, session=session, access_level=account.access_level)
        return JSONResponse(status_code=200, content={'message': 'Account created'})
    else:
        raise AccessException(needed_level=4, current_level=token_dict.access_level)

@router.post('/admin_delete')
async def admin_delete_account(request: Request,
                               login_info: LoginInfo,
                               session: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    token_dict = await check_login_cookies(request=request)
    if token_dict.access_level >= 4:
        await delete(login_info=login_info, session=session, soft=False)
        return JSONResponse(status_code=200, content={'message': 'Account deleted'})
    else:
        raise AccessException(needed_level=4, current_level=token_dict.access_level)
