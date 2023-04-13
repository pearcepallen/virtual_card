from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, validator

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

class Token(BaseModel):
    card_product_token: str
    user_token: str

class FundingSource(BaseModel):
    account_number: str #The ACH account number. Allowable Values: 36 char max
    account_type: str # The type of account. Allowable Values: checking, savings, corporate, loan
    bank_name: Optional[str] = None # The name of the financial institution where the ACH account is held. Allowable Values: 255 char max
    business_token: Optional[str] = None # Specifies the owner of the funding source. This token is required if a user_token is not specified. Allowable Values: 1–36 chars Send a GET request to /businesses to retrieve business tokens.
    is_default_account: Optional[bool] = None # If there are multiple funding sources, this field specifies which source is used by default in funding calls. If there is only one funding source, the system ignores this field and always uses that source. Allowable Values: true, false Default value: false
    name_on_account: str # Name on ACH account. Allowable Values: 1–50 chars
    routing_number: str # The routing number for the ACH account. Allowable Values: 9 digits
    token: str # The unique identifier of the funding source. If you do not include a token, the system will generate one automatically. This token is necessary for use in other calls, so we recommend that rather than let the system generate one, you use a simple string that is easy to remember. This value cannot be updated. Allowable Values: 1–36 chars
    user_token: Optional[str] = None # Specifies the owner of the funding source. This token is required if a business_token is not specified. Allowable Values: 1–36 chars Send a GET request to /users to retrieve user tokens.
    verification_notes: Optional[str] = None # Free-form text field for holding notes about verification. This field is returned only if verification_override = true. Allowable Values: 255 char max
    verification_overried: Optional[bool] = None # Allows the ACH funding source to be used regardless of its verification status. Allowable Values: true, false Default value: false

class TransactionCreate(BaseModel):
    card_token: str
    amount: Decimal
    currency: str

    @validator('currency')
    def validate_currency(cls, currency):
        if len(currency) != 3:
            raise ValueError("Currency must be exactly three characters")