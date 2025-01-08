from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .crud import get_user_by_id
from database import SessionLocal
import jwt
from dotenv import load_dotenv
import os
from util.get_parameter import get_parameter

router = APIRouter()

# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')

SECRET_KEY = get_parameter('/interviewdb-info/SECRET_KEY')
ALGORITHM = get_parameter('/interviewdb-info/ALGORITHM')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_bearer_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    encoded = authorization.split(" ")[1]
    try:
        payload = jwt.decode(encoded, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(get_bearer_token)):
    
    user = get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.user_name,
        "email": user.user_email,
    }

