from datetime import datetime

from pydantic import BaseModel

class TokenDict(BaseModel):
    """
    Contains id and access level
    """
    id: int
    access_level: int


class Account(BaseModel):
    """
    Pydantic class for user-inputted account details. \n
    Contains name, surname, email, password
    """
    username: str
    name: str
    surname: str
    email: str
    password: str

class AdminCreatedAccount(BaseModel):
    account: Account
    access_level: int

class LoginInfo(BaseModel):
    """
    Pydantic class for user-inputted login details. \n
    Contains username and password
    """
    email: str
    password: str


class AccountProcessed(BaseModel):
    """
    ORM-ready Pydantic class for precessed account details. \n
    Contains encrypted name with surname, encrypted email, hashed email, hashed password, id and username
    """
    id: int
    access_level_enc: str
    username_enc: str
    name_enc: str
    email_enc: str
    password_hash: str
    email_hash:  str
    is_active: bool

    model_config = {
        'from_attributes': True
    }

class VeryUnimportantRow(BaseModel):
    id: int
    text: str

    model_config = {
        'from_attributes': True
    }

class UnimportantRow(BaseModel):
    id: int
    text: str
    date: datetime

    model_config = {
        'from_attributes': True
    }


class ImportantRow(BaseModel):
    id: int
    text: str
    date: datetime
    amount: int

    model_config = {
        'from_attributes': True
    }