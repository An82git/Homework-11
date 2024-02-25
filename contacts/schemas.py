from pydantic import BaseModel, EmailStr, PastDate, field_validator
from typing import Optional


class ContactModel(BaseModel):
    name: str
    surname: str
    email_address: EmailStr
    phone_number: str
    birthday: PastDate
    additional_data: Optional[str] = None

    @field_validator("phone_number")
    def valid_number(cls, phone_number: str):
        number = phone_number.removeprefix("+")
        
        if number.isdigit() and len(number) == 11:
            if phone_number[0] != "+":
                phone_number = f"+{phone_number}"
            return phone_number
        raise ValueError("The phone number is invalid")

class ResponseContactsModel(ContactModel):
    id: int

class ResponseListContactsModel(BaseModel):
    contacts: list[ResponseContactsModel]

class DeleteContactModel(BaseModel):
    pass
