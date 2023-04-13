from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    city = Column(String)
    address1 = Column(String)
    address2 = Column(String, nullable=True)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)

    marqeta_card_token = Column(String, nullable=True)
    marqeta_user_token = Column(String, nullable=True)
    marqeta_cardproduct_token = Column(String, nullable=True)
    


# marqeta_token = relationship("MarqetaToken", back_populates="user")


# class Card(Base):
#     pass

# class Payment(Base):
#     pass

# class PlaidToken(Base):
#     pass

# class MarqetaToken(Base):
#     pass

# class Transactions(Base):
#     pass