from fastapi import HTTPException
from sqlalchemy.orm import Session

import app.models as models, app.schemas as schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email, 
        hashed_password=fake_hashed_password,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        city=user.city,        
        address1=user.address1,
        address2=user.address2,
        state=user.state,
        postal_code=user.postal_code,
        country=user.country,
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_field(db: Session, email: str, field_name: str, field_value: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    setattr(user, field_name, field_value)
    db.commit()
    db.refresh(user)
    return user

# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


