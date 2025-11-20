from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    jwt_secret: str = Field(default='12345', env='PYTHON_JWT_SECRET')
    email_secret: str = Field(default='12345', env='PYTHON_EMAIL_SECRET')
    name_secret : str = Field(default='12345', env='PYTHON_NAME_SECRET')

    postgres_engine: str = Field(default='postgresql+asyncpg', env='POSTGRES_ENGINE')
    postgres_db: str = Field(default='main', env='POSTGRES_DB')
    postgres_password: str = Field(default='12345', env='POSTGRES_PASSWORD')
    postgres_port: str = Field(default='5432', env='POSTGRES_PORT')
    postgres_user: str = Field(default='root', env='POSTGRES_USER')
    postgres_host: str = Field(default='localhost', env='POSTGRES_CONTAINER_NAME')

    redis_password: str = Field(default='12345', env='REDIS_PASSWORD')
    redis_port: str = Field(default='6379', env='REDIS_PORT')
    redis_host: str = Field(default='localhost', env='REDIS_CONTAINER_NAME')

settings=Settings()