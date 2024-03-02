from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, Depends, status, Security
from sqlalchemy.orm import Session

from src.schemas import UserSingupModel, UserResponse, TokenModel
from src.services.auth import auth_service
from src.repository.users import UsersDB
from src.database.db import get_db


router = APIRouter(prefix='/users', tags=["users"])
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserSingupModel,
    db: Session = Depends(get_db)
    ) -> UserResponse:

    exist_user = await UsersDB(db = db).get_user(username = body.username)
    
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    body.password = auth_service.get_password_hash(body.password)
    new_user = await UsersDB(db = db).create_user(body)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login")
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ) -> TokenModel:

    user = await UsersDB(db = db).get_user(username = body.username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = await auth_service.create_access_token(data={"sub": str(user.id)})
    refresh_token = await auth_service.create_refresh_token(data={"sub": str(user.id)})
    await UsersDB(db = db).update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
    ) -> TokenModel:
    
    token = credentials.credentials
    id = await auth_service.decode_refresh_token(token)
    user = await UsersDB(db = db).get_user(id = int(id))
    
    if user.refresh_token != token:
        await UsersDB(db = db).update_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": id})
    refresh_token = await auth_service.create_refresh_token(data={"sub": id})
    await UsersDB(db = db).update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
