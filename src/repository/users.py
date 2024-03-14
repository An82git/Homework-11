from sqlalchemy.orm import Session, Query
from datetime import datetime, UTC
from libgravatar import Gravatar

from src.database.models import Users
from src.schemas import UserSingupModel


class UsersDB:

    def __init__(self, db: Session) -> None:
        self.db = db
    
    async def get_users_objects(self) -> Query[Users]:
        return self.db.query(Users)
    
    async def filter_objects(self, objects: Query[Users], **kwargs) -> Query[Users]:
        for key, value in kwargs.items():
            if value:
                try:
                    objects = objects.filter(getattr(Users, key) == value)
                except AttributeError:
                    pass
        return objects

    async def get_users(self) -> list[Users]:
        users = await self.get_users_objects()
        return users.all()

    async def get_user(self, **kwargs) -> Users|None:
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
        user_obj.email = user.email
        user_obj.password = user.password

        self.db.add(user_obj)
        self.db.commit()
        self.db.refresh(user_obj)
        return user_obj

    async def delete_user(self, user_id) -> None:
        users_objects = await self.get_users_objects()
        filtered_users = await self.filter_objects(users_objects, id = user_id)
        filtered_users.delete()
        self.db.commit()

    async def update_token(self, user: Users, token: str | None) -> None:
        user.refresh_token = token
        self.db.commit()

    async def confirmed_email(self, email: str) -> None:
        user = await self.get_user(email = email)
        user.confirmed = True
        self.db.commit()

    async def update_avatar(self, user_id, url: str) -> Users:
        user = await self.get_user(id = user_id)
        user.avatar = url
        self.db.commit()
        return user
