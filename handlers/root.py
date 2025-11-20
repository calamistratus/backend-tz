from fastapi import APIRouter
from starlette.responses import FileResponse


router = APIRouter()

@router.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse("static/favicon.ico")