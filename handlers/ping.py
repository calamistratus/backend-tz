from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from database.repositories import AccountsRepository

router = APIRouter(prefix='/ping')

@router.get("/get_ids")
async def get_ids(session: AsyncSession = Depends(get_db_session)) -> dict:
    repo = AccountsRepository(session)
    ids = await repo.get_ids()
    return {'text' : str(ids)}