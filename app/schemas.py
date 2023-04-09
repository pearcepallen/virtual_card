from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    city: str
    address1: str
    address2: Optional[str] = None
    state: str
    postal_code: str
    country: str
    marqeta_card_token: str
    marqeta_user_token: str
    marqeta_cardproduct_token: str
    


class UserCreate(UserBase):
    password: str
    
    
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True        