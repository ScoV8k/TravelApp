from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from core.database import users_col
from api.models import PyObjectId, UserBase

from core.security import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class User(BaseModel):
    id: str
    email: str


async def authenticate_user(email: str, password: str):
    user = await users_col.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users_col.find_one({"_id": PyObjectId(user_id)})
    if not user:
        raise credentials_exception

    return User(id=str(user["_id"]), email=user["email"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserBase = Body(...)):
    """
    Rejestruje nowego użytkownika.
    - Sprawdza, czy użytkownik o podanym emailu już istnieje.
    - Hashuje hasło.
    - Zapisuje nowego użytkownika w bazie danych.
    - Zwraca token dostępowy do automatycznego zalogowania.
    """
    existing_user = await users_col.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik o tym adresie email już istnieje",
        )

    hashed_pwd = hash_password(user_data.password)
    
    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_pwd,
        "about": user_data.about,
        "created_at": datetime.utcnow()
    }

    result = await users_col.insert_one(new_user)
    created_user_id = result.inserted_id

    access_token = create_access_token(
        data={"sub": str(created_user_id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(created_user_id)
    }



@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": str(user["_id"])}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user["_id"])
    }
