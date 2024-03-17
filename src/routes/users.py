from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import Users
from src.repository.users import UsersDB
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/")
async def read_users_me(current_user: Users = Depends(auth_service.get_current_user)) -> UserModel:
    """
    Get the details of the current logged-in user.

    :param current_user: Current user object.
    :type current_user: Users
    :return: Details of the current user.
    :rtype: UserModel
    """
    return current_user


@router.patch('/avatar')
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: Users = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
    ) -> UserModel:
    """
    Update the avatar of the current logged-in user.

    :param file: Uploaded image file for the avatar.
    :type file: UploadFile
    :param current_user: Current user object.
    :type current_user: Users
    :param db: Database session dependency.
    :type db: Session
    :return: Updated user object with the new avatar URL.
    :rtype: UserModel
    """

    cloudinary.config(
        cloud_name = settings.cloudinary_name,
        api_key = settings.cloudinary_api_key,
        api_secret = settings.cloudinary_api_secret,
        secure = True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await UsersDB(db = db).update_avatar(current_user.id, src_url)
    return user
