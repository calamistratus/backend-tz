from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from database import get_db_session
from handlers.auth import check_login_cookies
from service.data_service import fetch


router = APIRouter(prefix='/service', tags=['service'])
frontend = Jinja2Templates(directory='frontend')

@router.get('/')
async def index_service(request: Request):
    response = frontend.TemplateResponse(
        'service.html',
        {'request': request},
    )
    await check_login_cookies(request=request, response=response)
    return response

@router.get('/fetch_data')
async def fetch_data(request: Request, repository_name: str, session: AsyncSession = Depends(get_db_session)):
    token_dict = await check_login_cookies(request=request)
    data = await fetch(session=session, repository_name=repository_name, access_level=token_dict.access_level)
    return JSONResponse(content=[i.model_dump_json() for i in data], status_code=200)

