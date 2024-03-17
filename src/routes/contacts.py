from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from datetime import date, timedelta

from src.schemas import ContactModel, ListContactsResponse, ContactResponse, DeleteContact, CreateContact, UpdateContact
from src.repository.contacts import ContactsDB
from src.services.auth import auth_service
from src.database.models import Users
from src.database.db import get_db


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", dependencies=[Depends(RateLimiter(times=4, seconds=1))])
async def get_contacts(
    name: str = "",
    surname: str = "",
    email_address: str = "",
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> ListContactsResponse:
    """
    Retrieve contacts for the current user with optional filtering by name, surname, or email address.

    :param name: Filter by name.
    :type name: str
    :param surname: Filter by surname.
    :type surname: str
    :param email_address: Filter by email address.
    :type email_address: str
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response containing a list of contacts.
    :rtype: ListContactsResponse
    """

    contacts = await ContactsDB(db = db).get_contacts(name = name, surname = surname, email_address = email_address, user = current_user.id)
    return {"contacts": contacts}


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=1, minutes=1))])
async def create_contact(
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> CreateContact:
    """
    Create a new contact for the current user.

    :param contact: Contact data to create.
    :type contact: ContactModel
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response containing the newly created contact.
    :rtype: CreateContact
    """
    
    new_contact = await ContactsDB(db = db).create_contact(current_user, contact)
    return {"contact": new_contact, "detail": "Contact successfully created"}


@router.get("/{contact_id}", dependencies=[Depends(RateLimiter(times=4, seconds=1))])
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> ContactResponse:
    """
    Retrieve the current user's contact by ID.

    :param contact_id: ID of the contact.
    :type contact_id: int
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response containing the contact information.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """

    contact = await ContactsDB(db = db).get_contact(current_user, contact_id)
    
    if contact is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Contact not found")
    
    return contact


@router.put("/{contact_id}", dependencies=[Depends(RateLimiter(times=1, minutes=1))])
async def update_contact(
    contact_id: int,
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> UpdateContact:
    """
    Update a specific contact by ID for the current user.

    :param contact_id: ID of the contact to update.
    :type contact_id: int
    :param contact: Updated contact data.
    :type contact: ContactModel
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response containing the updated contact information.
    :rtype: UpdateContact
    :raises HTTPException: If the specified contact is not found.
    """

    contact_obj = await ContactsDB(db = db).get_contact(current_user, contact_id)
    
    if contact_obj is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Contact not found")

    new_contact = await ContactsDB(db = db).update_contact(contact, contact_obj)
    return {"contact": new_contact, "detail": "Contact successfully updated"}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> DeleteContact:
    """
    Delete contact of current user by ID.

    :param contact_id: ID of the contact to delete.
    :type contact_id: int
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response indicating successful deletion of the contact.
    :rtype: DeleteContact
    """

    await ContactsDB(db = db).delete_contact(current_user, contact_id)
    return {"detail": "Contact successfully deleted"}


@router.get("/birthdays/{days_to_birthday}", dependencies=[Depends(RateLimiter(times=4, seconds=1))])
async def get_contacts_by_birthday(
    days_to_birthday: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(auth_service.get_current_user)
    ) -> ListContactsResponse:
    """
    Retrieve the contacts of the current user whose birthdays fall within the specified number of days from the current date.

    :param days_to_birthday: Number of days to include before the birthday.
    :type days_to_birthday: int
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Current user object.
    :type current_user: Users
    :return: Response containing a list of contacts with birthdays within the specified range.
    :rtype: ListContactsResponse
    """

    start_day = date.today()
    end_day = start_day + timedelta(days=days_to_birthday)
    contacts_obj = await ContactsDB(db = db).get_contacts(user = current_user.id)
    
    contact_list = []

    for contact in contacts_obj:
        if start_day.year % 4 != 0 and (contact.birthday.month == 2 and contact.birthday.day == 29):
            contact_date = date(start_day.year, contact.birthday.month, 28)
        else:
            contact_date = date(start_day.year, contact.birthday.month, contact.birthday.day)
        
        if start_day <= contact_date <= end_day:
            contact_list.append(contact)

        if start_day.year != end_day.year:
            contact_date = date(end_day.year, contact.birthday.month, contact.birthday.day)
        
            if start_day <= contact_date <= end_day:
                contact_list.append(contact)

    return {"contacts": contact_list}
