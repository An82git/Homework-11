from sqlalchemy.orm import Session, Query
from datetime import datetime, UTC
from libgravatar import Gravatar

from src.database.models import Users
from src.schemas import UserSingupModel


class UsersDB:
    """
    Handles database operations related to users.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
    
    async def get_users_objects(self) -> Query[Users]:
        """
        Retrieves all users from the database.

        :return: Query object for users.
        :rtype: Query[Users]
        """
        return self.db.query(Users)
    
    async def filter_objects(self, objects: Query[Users], **kwargs) -> Query[Users]:
        """
        Filters Query objects based on provided key-value pairs.

        :param objects: Query objects to filter.
        :type objects: Query[Users]
        :param kwargs: Key-value pairs for filtering.
        :type kwargs: dict
        :return: Filtered Query objects.
        :rtype: Query[Users]
        """
        for key, value in kwargs.items():
            if value:
                try:
                    objects = objects.filter(getattr(Users, key) == value)
                except AttributeError:
                    pass
        return objects

    async def get_users(self) -> list[Users]:
        """
        Retrieves all users.

        :return: List of users.
        :rtype: list[Users]
        """
        users = await self.get_users_objects()
        return users.all()

    async def get_user(self, **kwargs) -> Users|None:
        """
        Retrieves a specific user based on provided criteria.

        :param kwargs: Criteria for filtering users.
        :type kwargs: dict
        :return: User object if found, otherwise None.
        :rtype: Users | None
        """
        contacts = await self.get_users_objects()
        contact = await self.filter_objects(
            contacts,
            id = kwargs.get("id"),
            username = kwargs.get("username"),
            email = kwargs.get("email"),
            phone_number = kwargs.get("phone_number")
            )
        return contact.first()

    async def create_user(self, user: UserSingupModel) -> Users:
        """
        Creates a new user.

        :param user: UserSignupModel instance containing user data.
        :type user: UserSingupModel
        :return: Newly created user object.
        :rtype: Users
        """
        avatar = None

        try:
            g = Gravatar(user.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        new_contact = Users(
        username = user.username,
        email = user.email,
        phone_number = user.phone_number,
        password = user.password,
        avatar = avatar,
        created_at = datetime.now(UTC)
        )
    
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)
        return new_contact

    async def update_user(self, user: UserSingupModel, user_obj: Users) -> Users:
        """
        Updates an existing user.

        :param user: UserSingupModel instance containing updated user data.
        :type user: UserSingupModel
        :param user_obj: User object to update.
        :type user_obj: Users
        :return: Updated user object.
        :rtype: Users
        """
        user_obj.email = user.email
        user_obj.password = user.password

        self.db.add(user_obj)
        self.db.commit()
        self.db.refresh(user_obj)
        return user_obj

    async def delete_user(self, user_id: int) -> None:
        """
        Deletes a user.

        :param user_id: ID of the user to delete.
        :type user_id: int
        """
        user = await self.get_user(id = user_id)

        if user:
            self.db.delete(user)
            self.db.commit()

    async def update_token(self, user: Users, token: str | None) -> None:
        """
        Updates the refresh token for a user.

        :param user: User object.
        :type user: Users
        :param token: Refresh token.
        :type token: str | None
        """
        user.refresh_token = token
        self.db.commit()

    async def confirmed_email(self, email: str) -> None:
        """
        Marks user's email as confirmed.

        :param email: Email address of the user.
        :type email: str
        """
        user = await self.get_user(email = email)
        user.confirmed = True
        self.db.commit()

    async def update_avatar(self, user_id: int, url: str) -> Users:
        """
        Updates user's avatar URL.

        :param user_id: ID of the user.
        :type user_id: int
        :param url: New avatar URL.
        :type url: str
        :return: Updated user object.
        :rtype: Users
        """
        user = await self.get_user(id = user_id)
        user.avatar = url
        self.db.commit()
        return user
