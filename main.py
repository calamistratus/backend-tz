import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from database import AccountsRepository, get_db_session_cm, create_databases, create_mock_data
from exceptions import RedisPostgresException, init_exception_handlers, InputException
from handlers import routers
from schemas import Account
from service import process_account, account_to_login_info
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 30
    for i in range(max_retries):
        try:
            async with get_db_session_cm() as session:
                repo = AccountsRepository(session)
                admin_account = Account(
                    username='admin',
                    name='Administrator',
                    surname='Sidorovich',
                    email=settings.admin_email,
                    password=settings.admin_password,
                )
                try:
                    await AccountsRepository(session).check_login(account_to_login_info(admin_account))
                except InputException:
                    await repo.create_account(await process_account(admin_account, access_level=4))
                await create_databases()
                await repo.update_redis(is_setup=True)
                await create_mock_data(session)

            print("Redis updated with account ids")
            break
        except:
            traceback.print_exc()
            print('Postgres not ready yet')
            await asyncio.sleep(5)
    else:
        raise RedisPostgresException
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

init_exception_handlers(app)