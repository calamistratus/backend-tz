from sqlalchemy.ext.asyncio import AsyncSession

from database import VeryUnimportantDataRepository, AccountsRepository, UnimportantDataRepository, ImportantDataRepository
from exceptions import InputException
from schemas import Account
from service.conversions_service import unprocess_account


async def get_account(account_id: int, session: AsyncSession) -> Account:
    """
    Fetches an account from the repository by its id
    :param account_id: int
    :param session: AsyncSession object
    :return: Account object
    """
    repo = AccountsRepository(session=session)
    account = await repo.get_account_by_id(account_id)
    return unprocess_account(account)

async def fetch(session: AsyncSession,
                repository_name: str,
                access_level: int) -> list:
    """
    Fetches all rows from repository with repository_name
    :param session: AsyncSession object
    :param repository_name: str
    :param access_level: int
    :return:
    """
    match repository_name:
        case 'very_unimportant_data':
            repo = VeryUnimportantDataRepository(session)
        case 'unimportant_data':
            repo = UnimportantDataRepository(session)
        case 'important_data':
            repo = ImportantDataRepository(session)
        case 'accounts':
            repo = AccountsRepository(session)
        case _:
            raise InputException(invalid_field='repository_name')
    data = await repo.get_all(access_level=access_level)
    if repository_name == 'accounts':
        data = [unprocess_account(i) for i in data]
    return data