from sqlalchemy.orm import Session, Query

from src.database.models import Contacts, Users
from src.schemas import ContactModel


class ContactsDB:
    """
    Handles database operations related to contacts.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_contacts_objects(self) -> Query[Contacts]:
        """
        Retrieves all contacts from the database.

        :return: Query object for contacts.
        :rtype: Query[Contacts]
        """
        return self.db.query(Contacts)
    
    async def filter_objects(self, objects: Query[Contacts], **kwargs) -> Query[Contacts]:
        """
        Filters Query objects based on provided key-value pairs.

        :param objects: Query objects to filter.
        :type objects: Query[Contacts]
        :param kwargs: Key-value pairs for filtering.
        :type kwargs: dict
        :return: Filtered Query objects.
        :rtype: Query[Contacts]
        """
        for key, value in kwargs.items():
            if value:
                try:
                    objects = objects.filter(getattr(Contacts, key) == value)
                except AttributeError:
                    pass
        return objects

    async def get_contacts(self, **kwargs) -> list[Contacts]:
        """
        Retrieves contacts based on provided filters.

        :param kwargs: Filtering criteria.
        :type kwargs: dict
        :return: List of filtered contacts.
        :rtype: list[Contacts]
        """
        contacts = await self.get_contacts_objects()
        filtered_contacts = await self.filter_objects(
            contacts,
            name = kwargs.get("name"),
            surname = kwargs.get("surname"),
            email_address = kwargs.get("email_address"),
            user = kwargs.get("user")
        )
        return filtered_contacts.all()

    async def get_contact(self, user: Users, contact_id: int) -> Contacts|None:
        """
        Retrieves a specific contact belonging to a user.

        :param user: User object.
        :type user: Users
        :param contact_id: ID of the contact.
        :type contact_id: int
        :return: Contact object if found, otherwise None.
        :rtype: Contacts | None
        """
        contacts = await self.get_contacts_objects()
        contact = await self.filter_objects(contacts, user = user.id)
        return contact.order_by(Contacts.id).offset(contact_id - 1).first()

    async def create_contact(self, user: Users, contact: ContactModel) -> Contacts:
        """
        Creates a new contact for a user.

        :param user: User object.
        :type user: Users
        :param contact: Contact data.
        :type contact: ContactModel
        :return: Newly created contact object.
        :rtype: Contacts
        """
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

    async def update_contact(self, contact: ContactModel, contact_obj: Contacts) -> Contacts:
        """
        Updates an existing contact.

        :param contact: Updated contact data.
        :type contact: ContactModel
        :param contact_obj: Contact object to update.
        :type contact_obj: Contacts
        :return: Updated contact object.
        :rtype: Contacts
        """
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

    async def delete_contact(self, user: Users, contact_id: int) -> None:
        """
        Deletes a contact.

        :param user: User object.
        :type user: Users
        :param contact_id: ID of the contact to delete.
        :type contact_id: int
        """
        contact = await self.get_contact(user, contact_id)

        if contact:
            self.db.delete(contact)
            self.db.commit()
