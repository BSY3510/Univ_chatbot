from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.db import schemas
from app.db.session import SessionLocal

EMBEDDING_MODEL_NAME = 'jhgan/ko-sroberta-multitask'
KNOWLEDGE_BASE_PATH = "knowledge_base.pkl"

try:
    print("챗봇 API: 임베딩 모델 로드 중...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("챗봇 API: 임베딩 모델 로드 완료.")

    print(f"챗봇 API: 지식 베이스({KNOWLEDGE_BASE_PATH}) 로드 중...")
    with open(KNOWLEDGE_BASE_PATH, "rb") as f:
        knowledge_base = pickle.load(f)
    
    embeddings = knowledge_base["embeddings"]
    metadata = knowledge_base["metadata"]
    
    d = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(d)
    
    embeddings_np = np.array(embeddings).astype('float32')
 
    index.add(embeddings_np)
    
    print(f"챗봇 API: Faiss 인덱스 빌드 완료. (총 {len(embeddings)}개 벡터)")

except FileNotFoundError:
    print(f"[치명적 오류] 챗봇 API: {KNOWLEDGE_BASE_PATH} 파일을 찾을 수 없습니다.")
    model = None
    index = None
    metadata = []
except Exception as e:
    print(f"[치명적 오류] 챗봇 API: 모델 또는 데이터 로드 실패 - {e}")
    model = None
    index = None
    metadata = []

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chatbot", response_model=List[schemas.ChatbotResponse])
def get_chatbot_response(request: schemas.ChatbotRequest):
    if model is None or index is None:
        raise HTTPException(status_code=500, detail="챗봇 모델이 로드되지 않았습니다.")

    try:
        query_vector = model.encode([request.query], show_progress_bar=False)
        query_vector_np = np.array(query_vector).astype('float32')

        k = 3
        D, I = index.search(query_vector_np, k)

        results = []
        for i in I[0]:
            meta = metadata[i]
            results.append(schemas.ChatbotResponse(
                post_id=meta['post_id'],
                post_title=meta['post_title'],
                text=meta['text']
            ))
            
        return results

    except Exception as e:
        print(f"챗봇 응답 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail="챗봇 응답 생성 중 오류 발생")