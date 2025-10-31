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
    content: Optional[str] = None

class Post(PostBase):
    class Config:
        from_attributes = True 
        # orm_mode = True
        
class ChatbotRequest(BaseModel):
    query: str

class ChatbotResponse(BaseModel):
    post_id: int
    post_title: str
    text: str