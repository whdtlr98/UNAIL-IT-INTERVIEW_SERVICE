from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewPost(BaseModel):
    id: str  # 작성자 ID
    title: str
    content: Optional[str] = None

class PostList(BaseModel):
    idx: int
    id: str  
    title: str
    post_date: datetime

class Post(BaseModel):
    idx: int
    id: str  
    title: str
    content: Optional[str] = None
    post_date: datetime
    del_yn: str

class UpdatePost(BaseModel):
    idx: int
    title: str
    content: Optional[str] = None
