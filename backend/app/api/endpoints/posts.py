from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import pickle

from app.db import models, schemas
from app.db.session import SessionLocal

router = APIRouter()

try:
    with open("recommendation_model.pkl", "rb") as f:
        model_data = pickle.load(f)
    
    cosine_sim_matrix = model_data["cosine_sim_matrix"]
    id_to_index = model_data["id_to_index"]
    index_to_id = model_data["index_to_id"]
    print("추천 모델 로드 성공.")
except FileNotFoundError:
    print("[경고] 추천 모델 파일(recommendation_model.pkl)을 찾을 수 없습니다.")
    print("유사 게시물 추천 API가 작동하지 않습니다.")
    model_data = None

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

@router.get("/posts/{post_id}", response_model=schemas.Post)
def read_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")
    return post

@router.get("/posts/{post_id}/similar", response_model=List[schemas.Post])
def get_similar_posts(post_id: int, db: Session = Depends(get_db)):
    if model_data is None:
        print("모델이 로드되지 않아 유사 게시물을 반환할 수 없습니다.")
        return []
        
    try:
        if post_id not in id_to_index:
            print(f"게시물 ID {post_id}가 모델에 없습니다.")
            return []
            
        idx = id_to_index[post_id]

        sim_scores = list(enumerate(cosine_sim_matrix[idx]))

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        top_indices = [i[0] for i in sim_scores[1:6]]
        
        top_post_ids = [index_to_id[i] for i in top_indices]

        similar_posts = db.query(models.Post).filter(models.Post.id.in_(top_post_ids)).all()
        
        posts_map = {post.id: post for post in similar_posts}
        sorted_posts = [posts_map[id] for id in top_post_ids if id in posts_map]
        
        return sorted_posts

    except Exception as e:
        print(f"유사 게시물 추천 중 오류: {e}")
        raise HTTPException(status_code=500, detail="추천 중 오류 발생")