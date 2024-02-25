from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta

from schemas import ContactModel, ResponseListContactsModel, ResponseContactsModel, DeleteContactModel
from models import Contacts
from db import get_db


app = FastAPI()


@app.get("/api/contacts")
async def get_contacts(name: str = "", surname: str = "", email_address: str = "", db: Session = Depends(get_db)) -> ResponseListContactsModel:
    contacts = db.query(Contacts)

    if name:
        contacts = contacts.filter_by(name = name)
    if surname:
        contacts = contacts.filter_by(surname = surname)
    if email_address:
        contacts = contacts.filter_by(email_address = email_address)

    return {"contacts": contacts.all()}

@app.post("/api/contacts")
async def create_contact(contact: ContactModel, db: Session = Depends(get_db)) -> ResponseContactsModel:
    new_contact = Contacts(
        name = contact.name,
        surname = contact.surname,
        email_address = contact.email_address,
        phone_number = contact.phone_number,
        birthday = contact.birthday,
        additional_data = contact.additional_data
    )
    
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int, db: Session = Depends(get_db)) -> ResponseContactsModel:
    contact = db.query(Contacts).filter_by(id = contact_id).first()
    if contact is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Contact not found")
    return contact

@app.put("/api/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: ContactModel, db: Session = Depends(get_db)) -> ResponseContactsModel:
    contact_obj = db.query(Contacts).filter_by(id = contact_id).first()
    
    if contact_obj is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Contact not found")

    contact_obj.name = contact.name
    contact_obj.surname = contact.surname
    contact_obj.email_address = contact.email_address
    contact_obj.phone_number = contact.phone_number
    contact_obj.birthday = contact.birthday
    contact_obj.additional_data = contact.additional_data

    db.add(contact_obj)
    db.commit()
    db.refresh(contact_obj)
    return contact_obj

@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)) -> DeleteContactModel:
    contact_obj = db.query(Contacts).filter_by(id = contact_id)
    contact_obj.delete()
    db.commit()
    return {}

@app.get("/api/contacts/birthdays/{days_to_birthday}")
async def get_contacts_by_birthday(days_to_birthday: int, db: Session = Depends(get_db)) -> ResponseListContactsModel:
    start_day = date.today()
    end_day = start_day + timedelta(days=days_to_birthday)
    contacts_obj = db.query(Contacts).all()
    
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
