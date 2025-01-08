from sqlalchemy.orm import Session
from models import User, Interview, UserToken
from datetime import datetime  

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, name: str, email: str, id: str):
    db_user = User(
        name=name,
        email=email,
        id=id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, update_data: dict):
    db.query(User).filter(User.id == user_id).update(update_data)
    db.commit()

def get_interviews_by_user_id(db: Session, user_id: int):
    return db.query(Interview).filter(Interview.user_id == user_id).all()

def get_user_by_refresh_token(db: Session, user_id: int, refresh_token: str):
    user_token = db.query(UserToken).filter(
        UserToken.id == user_id,
        UserToken.refresh_token == refresh_token
    ).first()
    
    if user_token:
        return db.query(User).filter(User.id == user_id).first()
    return None

def update_user_refresh_token(db: Session, user_id: str, update_data: dict):
    user_token = db.query(UserToken).filter(UserToken.id == user_id).first()
    
    if user_token:
        user_token.refresh_token = update_data.get("refresh_token")
        user_token.refresh_token_created = datetime.utcnow() 
    else:
        new_user_token = UserToken(id=user_id, refresh_token=update_data.get("refresh_token"))
        db.add(new_user_token)
    
    db.commit()