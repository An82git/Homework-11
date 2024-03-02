from sqlalchemy.orm import Session, Query

from src.database.models import Contacts, Users
from src.schemas import ContactModel


class ContactsDB:

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_contacts_objects(self):
        return self.db.query(Contacts)
    
    async def filter_objects(self, objects: Query[Contacts], **kwargs):
        for key, value in kwargs.items():
            if value:
                try:
                    objects = objects.filter(getattr(Contacts, key) == value)
                except AttributeError:
                    pass
        return objects

    async def get_contacts(self, **kwargs):
        contacts = await self.get_contacts_objects()
        filtered_contacts = await self.filter_objects(
            contacts,
            name = kwargs.get("name"),
            surname = kwargs.get("surname"),
            email_address = kwargs.get("email_address"),
            user = kwargs.get("user")
        )
        return filtered_contacts.all()

    async def get_contact(self, user: Users, contact_id: int):
        
        # Не знаю як правильніше вчинити з id контакту для цього випадку,
        # чи шукати його за загальним id,
        # чи за номером розташування для user 

        contacts = await self.get_contacts_objects()

        # contact = await self.filter_objects(contacts, user = user.id, id = contact_id)
        # return contact.first()

        contact = await self.filter_objects(contacts, user = user.id)
        return contact.order_by(Contacts.id).offset(contact_id - 1).first()

    async def create_contact(self, user: Users, contact: ContactModel):
        new_contact = Contacts(
        name = contact.name,
        surname = contact.surname,
        email_address = contact.email_address,
        phone_number = contact.phone_number,
        birthday = contact.birthday,
        additional_data = contact.additional_data,
        user = user.id
        )
    
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)
        return new_contact

    async def update_contact(self, contact: ContactModel, contact_obj: Contacts):
        contact_obj.name = contact.name
        contact_obj.surname = contact.surname
        contact_obj.email_address = contact.email_address
        contact_obj.phone_number = contact.phone_number
        contact_obj.birthday = contact.birthday
        contact_obj.additional_data = contact.additional_data

        self.db.add(contact_obj)
        self.db.commit()
        self.db.refresh(contact_obj)
        return contact_obj

    async def delete_contact(self, user: Users, contact_id: int):
        contact = await self.get_contact(user, contact_id)

        if contact:
            self.db.delete(contact)
            self.db.commit()
