from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    
    url = Column(String(255), nullable=False)
    
    article_id = Column(String(50), nullable=False, index=True)

    university = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    
    created_at = Column(String(100), nullable=True)