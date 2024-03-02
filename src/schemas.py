from pydantic import BaseModel, EmailStr, PastDate, validator
from datetime import datetime
from typing import Optional


def valid_number(phone_number: str | None):
    if phone_number:
        number = phone_number.removeprefix("+")
        
        if number.isdigit() and len(number) == 11:
            if phone_number[0] != "+":
                phone_number = f"+{phone_number}"
            return phone_number
        raise ValueError("The phone number is invalid")


class ContactModel(BaseModel):
    name: str
    surname: str
    email_address: EmailStr
    phone_number: str
    birthday: PastDate
    additional_data: Optional[str] = None

    @validator('phone_number')
    def validate_phone_number(cls, phone_number):
        return valid_number(phone_number)
    

class ContactResponse(ContactModel):
    id: int

class ListContactsResponse(BaseModel):
    contacts: list[ContactResponse]

class CreateContact(BaseModel):
    contact: ContactResponse
    detail: str = "Contact successfully created"

class UpdateContact(BaseModel):
    contact: ContactResponse
    detail: str = "Contact successfully updated"

class DeleteContact(BaseModel):
    detail: str = "Contact successfully deleted"

class UserSingupModel(BaseModel):
    username: str
    email: Optional[str] = None
    phone_number: Optional[int] = None
    password: str

    @validator('phone_number')
    def validate_phone_number(cls, phone_number):
        return valid_number(phone_number)

class UserModel(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime

    @validator('phone_number')
    def validate_phone_number(cls, phone_number):
        return valid_number(phone_number)

class UserResponse(BaseModel):
    user: UserModel
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
