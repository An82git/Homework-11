import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import date

from src.database.models import Contacts, Users
from src.repository.contacts import ContactsDB
from src.schemas import ContactModel


class TestContactsDB(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):

        self.db = MagicMock(spec = Session)
        self.user = Users(id = 1)
        self.contacts = [
            Contacts(id = 0, user = self.user.id),
            Contacts(id = 1, name = "Bill"),
            Contacts(id = 2, name = "Bill", surname = "Smith"),
            Contacts()
        ]


    async def test_get_contacts_objects(self):

        self.db.query().all.return_value = self.contacts
        result = await ContactsDB(db = self.db).get_contacts_objects()
        self.assertEqual(self.contacts, result.all())


    async def test_filter_objects(self):

        self.db.query().filter().all.return_value = self.contacts[1:3]
        result = await ContactsDB(db = self.db).filter_objects(self.db.query(), name = "Bill")
        self.assertEqual(self.contacts[1:3], result.all())

        self.db.query().filter().all.return_value = [self.contacts[2]]
        result = await ContactsDB(db = self.db).filter_objects(self.db.query(), surname = "Smith")
        self.assertEqual([self.contacts[2]], result.all())

        self.db.query().all.return_value = self.contacts
        result = await ContactsDB(db = self.db).filter_objects(self.db.query())
        self.assertEqual(self.contacts, result.all())


    async def test_get_contacts(self):

        self.db.query().all.return_value = []
        result = await ContactsDB(db = self.db).get_contacts()
        self.assertEqual([], result)

        self.db.query().filter().all.return_value = [self.contacts[0]]
        result = await ContactsDB(db = self.db).get_contacts(user = self.user.id)
        self.assertEqual([self.contacts[0]], result)
        
        self.db.query().filter().filter().all.return_value = []
        result = await ContactsDB(db = self.db).get_contacts(user = self.user.id, surname = "Smith")
        self.assertEqual([], result)


    async def test_get_contact(self):

        self.db.query().filter().order_by().offset().first.return_value = self.contacts[0]
        result = await ContactsDB(db = self.db).get_contact(user = self.user, contact_id = 0)
        self.assertEqual(self.contacts[0], result)

        self.db.query().filter().order_by().offset().first.return_value = None
        result = await ContactsDB(db = self.db).get_contact(user = self.user, contact_id = 1)
        self.assertEqual(None, result)


    async def test_create_contact(self):

        contact = ContactModel(
            name = "Steve",
            surname = "Johnson",
            email_address = "stevejohnson@test.com",
            phone_number = "01234567899",
            birthday = date(2023, 3, 17),
            additional_data = None
        )

        result = await ContactsDB(db = self.db).create_contact(user = self.user, contact = contact)
        self.assertEqual(contact.name, result.name)
        self.assertEqual(contact.surname, result.surname)
        self.assertEqual(contact.email_address, result.email_address)
        self.assertEqual(contact.phone_number, result.phone_number)
        self.assertEqual(contact.birthday, result.birthday)
        self.assertEqual(contact.additional_data, result.additional_data)
        self.assertTrue(hasattr(result, "id"))


    async def test_update_contact(self):

        contact = ContactModel(
            name = "Steve",
            surname = "Johnson",
            email_address = "stevejohnson@test.com",
            phone_number = "01234567899",
            birthday = date(2023, 3, 17),
            additional_data = None
        )

        result = await ContactsDB(db = self.db).update_contact(contact = contact, contact_obj = self.contacts[3])
        self.assertEqual(contact.name, result.name)
        self.assertEqual(contact.surname, result.surname)
        self.assertEqual(contact.email_address, result.email_address)
        self.assertEqual(contact.phone_number, result.phone_number)
        self.assertEqual(contact.birthday, result.birthday)
        self.assertEqual(contact.additional_data, result.additional_data)
        self.assertTrue(hasattr(result, "id"))


    async def test_delete_contact(self):

        self.db.query().filter().order_by().offset().first.return_value = self.contacts[0]
        result = await ContactsDB(db = self.db).delete_contact(user = self.user, contact_id = 0)
        self.db.delete.assert_called_once_with(self.contacts[0])
        self.assertIsNone(result)

        self.db.query().filter().order_by().offset().first.return_value = None
        result = await ContactsDB(db = self.db).delete_contact(user = self.user, contact_id = 1)
        self.assertIsNone(result)
        