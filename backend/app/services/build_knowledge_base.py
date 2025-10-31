import pickle
import pandas as pd
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.db.session import SessionLocal, engine
from app.db.models import Post
from app.db import models

EMBEDDING_MODEL_NAME = 'jhgan/ko-sroberta-multitask'

def build_knowledge_base():
    print(f"'{EMBEDDING_MODEL_NAME}' 모델을 로드합니다... (시간이 걸릴 수 있음)")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("챗봇 지식 베이스 빌드를 시작합니다...")
    db: Session = SessionLocal()
    try:
        posts = db.query(Post.id, Post.title, Post.content).all()
        if not posts:
            print("오류: DB에 게시물이 없습니다.")
            return

        print(f"총 {len(posts)}개의 게시물을 처리합니다.")

        chunks = []
        metadata = []

        for post in posts:
            if not post.content:
                continue

            paragraphs = post.content.split('\n')
            
            for para in paragraphs:
                para = para.strip()
                if len(para) > 10: 
                    chunks.append(para)
                    metadata.append({
                        'post_id': post.id,
                        'post_title': post.title,
                        'text': para
                    })

        if not chunks:
            print("오류: 유효한 텍스트 조각(chunk)을 찾을 수 없습니다.")
            return

        print(f"총 {len(chunks)}개의 텍스트 조각을 임베딩합니다...")

        embeddings = model.encode(chunks, show_progress_bar=True)

        knowledge_base_data = {
            "embeddings": embeddings,
            "metadata": metadata
        }

        with open("knowledge_base.pkl", "wb") as f:
            pickle.dump(knowledge_base_data, f)
            
        print("지식 베이스 빌드 및 저장 완료: knowledge_base.pkl")

    except Exception as e:
        print(f"지식 베이스 빌드 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    build_knowledge_base()