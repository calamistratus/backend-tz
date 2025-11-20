from pydantic import BaseModel

class Account(BaseModel):
    """
    Pydantic class for user-inputted account details. \n
    Contains name, surname, email, password
    """
    name: str
    surname: str
    email: str
    password: str


class AccountProcessed(BaseModel):
    """
    ORM-ready Pydantic class for precessed account details. \n
    Contains encrypted name with surname, encrypted email, hashed email, hashed password, id and username
    """
    id: int
    username: str
    name_enc: str
    email_enc: str
    password_hash: str
    email_hash:  str

    model_config = {
        'from_attributes': True
    }