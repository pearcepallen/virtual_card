import base64
from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv, find_dotenv
import os

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status, requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine

import requests

import app.crud as crud, app.models as models, app.schemas as schemas

SECRET_KEY = "5930f5a8c89131b4cbe8dff7b30481fc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

load_dotenv(find_dotenv())

models.Base.metadata.create_all(bind=engine)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "test": {
     "token": "0e2f740d-d823-46ae-b7f3-e963dfc97d09", 
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



app = FastAPI()

# Dependency for the database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db=get_db(), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(get_db(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


# @app.get("/users/me/items/")
# async def read_own_items(current_user: Annotated[User, Depends(get_current_active_user)]):
#     return [{"item_id": "Foo", "owner": current_user.username}]

@app.post("/users")
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):    
    return crud.create_user(db=db, user=user)

@app.get("/users/{email}")
async def get_user_by_email(email: str, db: Session = Depends(get_db)):    
    return crud.get_user_by_email(db=db, email=email)

@app.put("/users/{email}/{field_name}/")
async def update_user_field(data:dict, email:str, field_name: str, db: Session = Depends(get_db)):    
    return crud.update_user_field(db=db, email=email, field_name=field_name, field_value=data["value"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/marqeta/users/")
async def create_marqeta_user(user: dict):
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/users"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    data = {
        "address1": user["address1"],
        "city": user["city"],
        "state": user["state"],
        "postal_code": user["postal_code"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "country": user["country"]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.get("/marqeta/users/{token}")
async def get_marqeta_user(token: str):
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/users/{token}"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

@app.post("/marqeta/cardproducts/")
async def create_marqeta_cardproduct():
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/cardproducts"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    start_d =  date.today().strftime('%Y-%m-%d')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }    
    data = {
            "name": "virtual card",
            "start_date": "2019-08-24",
            "config": {
                "card_life_cycle": {
                    "activate_upon_issue": True
                },
                "fulfillment": {
                    "payment_instrument": "VIRTUAL_PAN"
                }
            }
        }    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.get("/marqeta/cardproducts/{token}")
async def get_marqeta_cardproduct(token: str):
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/cardproducts/{token}"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

@app.post("/marqeta/cards/")
async def create_marqeta_card(tokens: dict):
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/cards"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    data = {
        "card_product_token": tokens["card_product_token"],
        "user_token": tokens["user_token"],    
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.get("/marqeta/cards/{token}")
async def get_marqeta_card(token: str):
    base_url = os.environ["MARQETA_BASE_URL"]
    url = f"{base_url}/cards/{token}"
    username = os.environ['MARQETA_API_TOKEN']
    password = os.environ['MARQETA_ADMIN_TOKEN']
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    response = requests.get(url, headers=headers)
    return response.json()