from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import FileResponse, Response
from fastapi.templating import Jinja2Templates

from database.repositories import check_access_level
from exceptions import AccessException
from handlers.auth import check_login_cookies

router = APIRouter(tags=['root'])
frontend = Jinja2Templates(directory='frontend')

@router.get('/')
async def index(request: Request):
    response = frontend.TemplateResponse(
        'index.html',
        {'request': request},
    )
    await check_login_cookies(request=request, response=response)
    return response

@router.get('/admin')
async def index_admin(request: Request):
    token_dict = await check_login_cookies(request=request)
    if token_dict.access_level >= 4:
        response = frontend.TemplateResponse(
            'admin.html',
            {'request': request},
        )
        return response
    else:
        raise AccessException(needed_level=4, current_level=token_dict.access_level)

@router.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse("static/favicon.ico")