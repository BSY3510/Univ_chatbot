from pydantic import BaseModel
from typing import Optional

class PostBase(BaseModel):
    id: int
    title: str
    url: str
    author: Optional[str] = None
    created_at: Optional[str] = None
    university: str
    department: str
    category: str
    article_id: str

class Post(PostBase):
    class Config:
        from_attributes = True 
        # orm_mode = True