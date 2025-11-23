from fastapi.responses import JSONResponse
from fastapi.requests import Request

class RedisPostgresException(Exception):
    """There was an error contacting postgres/redis"""
    pass


class LoginException(Exception):
    """Could neither create a temp account nor login"""
    def __init__(self, message: str):
        super().__init__(message)
    pass


class LoginExpiredException(Exception):
    """Token was expired"""
    pass


class LoginInvalidException(Exception):
    """The provided login was invalid"""
    pass


class AccessException(Exception):
    """
    You do not have permission to access this page \n
    """
    access_levels = {
        -1: 'None',
        0: 'Unregistered user',
        1: 'Registered user',
        2: 'Verified',
        3: 'Contributor',
        4: 'Admin',
        5: 'Root'
    }

    def __init__(self, needed_level: int, current_level: int):
        message = (
            f'Currently, you are "{self.access_levels[current_level]}", '
            f'But you need to be "{self.access_levels[needed_level]}" to use this'
        )

        super().__init__(message)


class InputException(Exception):
    """There was an error with input"""
    def __init__(self, invalid_field: str):
        self.message = f'The {invalid_field} was invalid'
        super().__init__(self.message)
    pass


class EmailTakenException(Exception):
    """This username was already taken"""
    def __init__(self):
        self.message = f'The email was already taken, please, use another one'
        super().__init__(self.message)


def init_exception_handlers(app):
    @app.exception_handler(EmailTakenException)
    async def handle_email_exc(request: Request, exc: EmailTakenException):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    @app.exception_handler(AccessException)
    async def handle_access_exc(request: Request, exc: AccessException):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
        )
    @app.exception_handler(InputException)
    async def handle_input_exc(request: Request, exc: InputException):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )