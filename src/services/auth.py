from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, UTC
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.repository.users import UsersDB
from src.database.models import Users
from src.conf.config import settings
from src.database.db import get_db


class Auth:
    """
    Class for handling authentication related operations.
    """
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self) -> None:
        self.SECRET_KEY = settings.secret_key
        self.ALGORITHM = settings.algorithm

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify whether the provided plain password matches the hashed password.

        :param plain_password: Plain text password.
        :type plain_password: str
        :param hashed_password: Hashed password.
        :type hashed_password: str
        :return: Boolean indicating whether the passwords match.
        :rtype: bool
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generates a hashed version of the provided password.

        :param password: Password to hash.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """

        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates an access token based on the provided data.

        :param data: Data to encode into the token.
        :type data: dict
        :param expires_delta: Optional expiration delta for the token.
        :type expires_delta: float, optional
        :return: Encoded access token.
        :rtype: str
        """

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(minutes=60)

        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates a refresh token based on the provided data.

        :param data: Data to encode into the token.
        :type data: dict
        :param expires_delta: Optional expiration delta for the token.
        :type expires_delta: float, optional
        :return: Encoded refresh token.
        :rtype: str
        """

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(days=7)

        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decode the provided refresh token and return the user ID.

        :param refresh_token: Refresh token to decode.
        :type refresh_token: str
        :return: Decoded user ID.
        :rtype: str
        :raises HTTPException: If the token's scope is invalid or the credentials cannot be validated.
        """

        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                id = payload['sub']
                return id
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Users:
        """
        Retrieve the current user based on the provided access token.

        :param token: Access token.
        :type token: str
        :param db: Database session dependency.
        :type db: Session
        :return: Current user object.
        :rtype: Users
        :raises HTTPException: If the credentials cannot be validated or the user is not found.
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                id = payload["sub"]
                if id is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await UsersDB(db = db).get_user(id = int(id))
        if user is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict) -> str:
        """
        Creates a token for email verification based on the provided data.

        :param data: Data to encode into the token.
        :type data: dict
        :return: Encoded email verification token.
        :rtype: str
        """

        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Decodes the provided email verification token and return the email address.

        :param token: Email verification token.
        :type token: str
        :return: Decoded email address.
        :rtype: str
        :raises HTTPException: If the token is invalid for email verification.
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
