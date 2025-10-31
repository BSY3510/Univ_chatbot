from pydantic import BaseModel
from typing import Optional, List

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

class ChatbotRequest(BaseModel):
    query: str

class ChatbotSource(BaseModel):
    post_id: int
    post_title: str
    text: str

class GeminiChatbotResponse(BaseModel):
    answer: str
    sources: List[ChatbotSource]