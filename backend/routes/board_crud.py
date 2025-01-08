from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Board  # SQLAlchemy 모델
from routes.board_schema import NewPost, PostList, Post, UpdatePost

# 게시글 생성
def insert_post(new_post: NewPost, db: Session):
    post = Board(
        id=new_post.id,
        title=new_post.title,
        content=new_post.content,
        del_yn='Y', 
    )
    db.add(post)
    db.commit()
    return post.idx

def list_all_post(db: Session):
    posts = db.query(Board).filter(Board.del_yn == 'Y').all()
    return [
        PostList(
            idx=row.idx,
            id=row.id,
            title=row.title,
            post_date=row.post_date
        )
        for row in posts
    ]

def get_post(post_idx: int, db: Session):
    post = db.query(Board).filter(and_(Board.idx == post_idx, Board.del_yn == 'Y')).first()
    if not post:
        return {"error": "존재하지 않는 게시글 번호입니다."}
    return Post(
        idx=post.idx,
        id=post.id,
        title=post.title,
        content=post.content,
        post_date=post.post_date,
        del_yn=post.del_yn,
    )

# 게시글 수정
def update_post(update_post: UpdatePost, db: Session):
    post = db.query(Board).filter(and_(Board.idx == update_post.idx, Board.del_yn == 'Y')).first()
    if not post:
        return {"error": "존재하지 않는 게시글 번호입니다."}
    post.title = update_post.title
    post.content = update_post.content
    db.commit()
    return get_post(post.idx, db)

# 게시글 상태 변경 (del_yn = 'N')
def alter_del_yn(post_idx: int, db: Session):
    post = db.query(Board).filter(and_(Board.idx == post_idx, Board.del_yn == 'Y')).first()
    if not post:
        return {"error": "존재하지 않는 게시글 번호입니다."}
    post.del_yn = 'N'
    db.commit()
    return {"msg": "삭제가 완료되었습니다."}

# 게시글 영구 삭제
def delete_post(post_idx: int, db: Session):
    post = db.query(Board).filter(Board.idx == post_idx).first()
    if not post:
        return {"error": "존재하지 않는 게시글 번호입니다."}
    db.delete(post)
    db.commit()
    return {"msg": "게시글이 영구적으로 삭제되었습니다."}
