# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, UserRegister
from database import SessionLocal


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == id).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="해당 고유 아이디는 이미 존재합니다.")
    
    new_user = User(
        user_name=user.name,
        user_email=user.email,
        user_joined=user.user_joined, 
        id=user.id,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입이 완료되었습니다."}
