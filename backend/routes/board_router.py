from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .auth import get_db  # DB 세션 의존성
from routes import board_crud, board_schema
from models import Board

router = APIRouter(prefix="/board")

@router.post("/create", description="게시글 생성")
async def create_new_post(new_post: board_schema.NewPost, db: Session = Depends(get_db)):
    return {"post_id": board_crud.insert_post(new_post, db)}

@router.get("/read", description="전체 게시글 조회")
async def read_all_posts(db: Session = Depends(get_db)):
    return board_crud.list_all_post(db)

@router.get("/read/{post_idx}", description="특정 게시글 조회")
async def read_post(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.get_post(post_idx, db)

@router.put("/update", description="게시글 수정")
async def update_post(update_post: board_schema.UpdatePost, db: Session = Depends(get_db)):
    return board_crud.update_post(update_post, db)

@router.patch("/delete/{post_idx}", description="게시글 상태 변경")
async def delete_post_yn(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.alter_del_yn(post_idx, db)

@router.delete("/delete/{post_idx}", description="게시글 영구 삭제")
async def delete_post(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.delete_post(post_idx, db)


@router.get("/api/all-board-ids")
def get_all_board_ids(db: Session = Depends(get_db)):
    board_ids = db.query(Board.idx).all()
    result = [id[0] for id in board_ids]
    print(result) 
    return result