import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.users import UsersDB
from src.schemas import UserSingupModel
from src.database.models import Users


class TestUsersDB(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec = Session)
        self.users = [
            Users(id = 0, refresh_token = "refresh_token"),
            Users(id = 1, username = "Emily Johnson"),
            Users(id = 2, username = "William Anderson", email = "williamanderson@test.com"),
            Users()
        ]

    async def test_get_contacts_objects(self):

        self.db.query().all.return_value = self.users
        result = await UsersDB(db = self.db).get_users_objects()
        self.assertEqual(self.users, result.all())


    async def test_filter_objects(self):

        self.db.query().filter().all.return_value = [self.users[2]]
        result = await UsersDB(db = self.db).filter_objects(self.db.query(), id = 2)
        self.assertEqual([self.users[2]], result.all())

        self.db.query().filter().all.return_value = [self.users[1]]
        result = await UsersDB(db = self.db).filter_objects(self.db.query(), username = "Emily Johnson")
        self.assertEqual([self.users[1]], result.all())
        

    async def test_get_users(self):

        self.db.query().all.return_value = self.users
        result = await UsersDB(db = self.db).get_users()
        self.assertEqual(self.users, result)


    async def test_get_user(self):
        
        self.db.query().filter().first.return_value = self.users[1]
        result = await UsersDB(db = self.db).get_user(id = 1)
        self.assertEqual(self.users[1], result)

        self.db.query().filter().first.return_value = None
        result = await UsersDB(db = self.db).get_user(id = 4)
        self.assertEqual(None, result)


    async def test_create_user(self):

        user = UserSingupModel(
            username = "Olivia Martinez",
            email = "oliviamartinez@test.com",
            phone_number = None,
            password = "password"
        )

        result = await UsersDB(db = self.db).create_user(user = user)
        self.db.commit.assert_called_once_with()
        self.assertEqual(user.username, result.username)
        self.assertEqual(user.email, result.email)
        self.assertEqual(user.password, result.password)
        self.assertEqual(user.phone_number, result.phone_number)
        self.assertTrue(hasattr(result, "id"))


    async def test_update_user(self):

        user = UserSingupModel(
            username = "Olivia Martinez",
            email = "oliviamartinez@test.com",
            phone_number = None,
            password = "password"
        )

        result = await UsersDB(db = self.db).update_user(user = user, user_obj = self.users[3])
        self.db.commit.assert_called_once_with()
        self.assertEqual(self.users[3].username, result.username)
        self.assertEqual(user.email, result.email)
        self.assertEqual(user.password, result.password)
        self.assertEqual(self.users[3].phone_number, result.phone_number)
        self.assertEqual(self.users[3].id, result.id)


    async def test_delete_user(self):

        self.db.query().filter().first.return_value = self.users[2]
        result = await UsersDB(db = self.db).delete_user(user_id = 2)
        self.db.delete.assert_called_once_with(self.users[2])
        self.db.commit.assert_called_once_with()
        self.assertIsNone(result)

        self.db.query().filter().first.return_value = None
        result = await UsersDB(db = self.db).delete_user(user_id = 4)
        self.db.commit.assert_called_once_with()
        self.assertIsNone(result)


    async def test_update_token(self):

        result = await UsersDB(db = self.db).update_token(user = self.users[0], token = "token")
        self.db.commit.assert_called_once_with()
        self.assertEqual(self.users[0].refresh_token, "token")


    async def test_confirmed_email(self):
        
        self.db.query().filter().first.return_value = self.users[2]
        result = await UsersDB(db = self.db).confirmed_email(self.users[2].email)
        self.db.commit.assert_called_once_with()
        self.assertTrue(self.users[2].confirmed)


    async def test_update_avatar(self):

        self.db.query().filter().first.return_value = self.users[1]
        result = await UsersDB(db = self.db).update_avatar(user_id = 1, url = "https://avatar")
        self.db.commit.assert_called_once_with()
        self.assertEqual(self.users[1].avatar, "https://avatar")
