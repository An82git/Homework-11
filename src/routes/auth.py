from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from sqlalchemy.orm import Session

from src.schemas import UserSingupModel, UserResponse, TokenModel, RequestEmail, StringResponse
from src.services.auth import auth_service
from src.services.email import send_email
from src.repository.users import UsersDB
from src.database.db import get_db


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    background_tasks: BackgroundTasks,
    body: UserSingupModel,
    request: Request,
    db: Session = Depends(get_db)
    ) -> UserResponse:

    exist_user = await UsersDB(db = db).get_user(email = body.email)
    
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    body.password = auth_service.get_password_hash(body.password)
    new_user = await UsersDB(db = db).create_user(body)

    background_tasks.add_task(send_email, body.email, body.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login")
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ) -> TokenModel:

    user = await UsersDB(db = db).get_user(username = body.username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = await auth_service.create_access_token(data={"sub": str(user.id)})
    refresh_token = await auth_service.create_refresh_token(data={"sub": str(user.id)})
    await UsersDB(db = db).update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh-token')
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


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> StringResponse:
    email = await auth_service.get_email_from_token(token)
    user = await UsersDB(db = db).get_user(email = email)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    await UsersDB(db = db).confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
    ) -> StringResponse:

    user = await UsersDB(db = db).get_user(email = body.email)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)

    return {"message": "Check your email for confirmation."}
