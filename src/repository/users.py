from sqlalchemy.orm import Session, Query
from datetime import datetime

from src.database.models import Users
from src.schemas import UserSingupModel


class UsersDB:

    def __init__(self, db: Session) -> None:
        self.db = db
    
    async def get_users_objects(self):
        return self.db.query(Users)
    
    async def filter_objects(self, objects: Query[Users], **kwargs):
        for key, value in kwargs.items():
            if value:
                try:
                    objects = objects.filter(getattr(Users, key) == value)
                except AttributeError:
                    pass
        return objects

    async def get_users(self, ):
        users = await self.get_users_objects()
        return users.all()

    async def get_user(self, **kwargs):
        contacts = await self.get_users_objects()
        contact = await self.filter_objects(
            contacts,
            id = kwargs.get("id"),
            username = kwargs.get("username"),
            email = kwargs.get("email"),
            phone_number = kwargs.get("phone_number")
            )
        return contact.first()

    async def create_user(self, contact: UserSingupModel):
        new_contact = Users(
        username = contact.username,
        email = contact.email,
        phone_number = contact.phone_number,
        password = contact.password,
        created_at = datetime.utcnow()
        )
    
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)
        return new_contact

    async def update_user(self, contact: UserSingupModel, contact_obj: Users):
        contact_obj.email = contact.email
        contact_obj.password = contact.password

        self.db.add(contact_obj)
        self.db.commit()
        self.db.refresh(contact_obj)
        return contact_obj

    async def delete_user(self, user_id):
        contacts_objects = await self.get_users_objects()
        filtered_contacts = await self.filter_objects(contacts_objects, id = user_id)
        filtered_contacts.delete()
        self.db.commit()

    async def update_token(self, user: Users, token: str | None):
        user.refresh_token = token
        self.db.commit()
