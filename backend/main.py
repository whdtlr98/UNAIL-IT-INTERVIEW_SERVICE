from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.transcribe import router as transcribe_router
from routes.kakao import router as kakao_router
from routes.auth import router as auth_router
from routes.interview import router as interview_router
from routes.userinfo import router as userinfo_router

from routes import board_router  
from database import init_db


load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.aiunailit.com","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()

app.include_router(board_router.router, tags=["board"])  
app.include_router(auth_router, tags=["auth"])
app.include_router(transcribe_router, tags=["interview"])
app.include_router(kakao_router, tags=["auth"])
app.include_router(interview_router,tags=["interview"] )
app.include_router(userinfo_router, tags=["user"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

