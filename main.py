import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from database import AccountsRepository, get_db_session_cm
from exceptions import RedisPostgresException
from handlers import routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 30
    for i in range(max_retries):
        try:
            async with get_db_session_cm() as session:
                repo = AccountsRepository(session)
                await repo.update_redis()
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