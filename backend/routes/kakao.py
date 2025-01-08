from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import httpx
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_user_by_id, update_user,get_user_by_refresh_token, update_user_refresh_token
from models import User
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
from util.get_parameter import get_parameter


router = APIRouter()

load_dotenv()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# kakao_client_id = os.getenv('KAKAO_CLIENT_ID')
kakao_redirect_uri = 'http://localhost:3000/oauth/callback/kakao'

kakao_client_id = get_parameter('/interviewdb-info/kakao/KAKAO_CLIENT_ID')
# kakao_redirect_uri = get_parameter('/interviewdb-info/kakao/KAKAO_REDIRECT_URI')

ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 1 


# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')

SECRET_KEY = get_parameter('/interviewdb-info/SECRET_KEY')
ALGORITHM = get_parameter('/interviewdb-info/ALGORITHM')


@router.get("/login/oauth/code/kakao")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    try:
        user_count = db.query(User).count()  
        print(user_count)
        print(kakao_redirect_uri)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 연결 실패: {str(e)}")

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": kakao_client_id,
        "redirect_uri": kakao_redirect_uri,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        user_response = await client.get(user_info_url, headers=headers)
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        user_info = user_response.json()
        kakao_id = user_info['id'] 
        existing_user = get_user_by_id(db=db, user_id=int(kakao_id))

    if existing_user:

        access_token_expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_access_token_encode = {
            'type': 'access_token',
            'userId': kakao_id,
            'iat': datetime.utcnow(),
            'exp': access_token_expiry 
        }


        encoded_access_token_jwt = jwt.encode(to_access_token_encode, SECRET_KEY, algorithm=ALGORITHM)
        refresh_token_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_refresh_token_encode = {
            'type': 'refresh_token',
            'userId': kakao_id,
            'iat': datetime.utcnow(),
            'exp': refresh_token_expiry 
        }

        encoded_refresh_token_jwt = jwt.encode(to_refresh_token_encode, SECRET_KEY, algorithm=ALGORITHM)

        update_user_refresh_token(db, existing_user.id, {
            "refresh_token": encoded_refresh_token_jwt,
        })
        
        
        response = JSONResponse(content={
            "message": "로그인 성공", 
            "user": {
                "id": kakao_id,
                "name": existing_user.user_name, 
                "email": existing_user.user_email,
                "access_token": encoded_access_token_jwt,
                "refresh_token": encoded_refresh_token_jwt
            },
        })
        return response
    
    return JSONResponse(content={
        "message": "회원가입 필요",
        "kakao_id": kakao_id,
        "name": user_info['properties']['nickname'],
    })


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("userId")
        
        user = get_user_by_refresh_token(db, user_id, refresh_token)
        if not user:
            raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")
        
        access_token_expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = {
            'type': 'access_token',
            'userId': user_id,
            'iat': datetime.utcnow(),
            'exp': access_token_expiry
        }
        
        encoded_access_token = jwt.encode(new_access_token, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": encoded_access_token}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")