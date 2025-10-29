from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import models, schemas
from app.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/posts", response_model=List[schemas.Post])
def read_posts(
    department: Optional[str] = None,
    skip: int = 0, 
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(models.Post)
    
    if department:
        query = query.filter(models.Post.department == department)
    
    posts = (
        query.order_by(models.Post.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts