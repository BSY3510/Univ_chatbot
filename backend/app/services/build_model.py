import pickle
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.db.session import SessionLocal, engine
from app.db.models import Post
from app.db import models

# models.Base.metadata.create_all(bind=engine)

def build_recommendation_model():
    print("유사 게시물 추천 모델 빌드를 시작합니다...")
    
    db: Session = SessionLocal()
    try:
        posts_query = db.query(Post).all()
        if not posts_query:
            print("오류: DB에 게시물이 없습니다.")
            return

        posts_df = pd.DataFrame([p.__dict__ for p in posts_query])
        
        posts_df['content'] = posts_df['content'].fillna('')

        print(f"총 {len(posts_df)}개 게시물로 모델을 학습합니다.")

        tfidf_vectorizer = TfidfVectorizer(min_df=5, ngram_range=(1, 2))
        tfidf_matrix = tfidf_vectorizer.fit_transform(posts_df['content'])

        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        id_to_index = dict(zip(posts_df['id'], posts_df.index))

        model_data = {
            "vectorizer": tfidf_vectorizer,
            "cosine_sim_matrix": cosine_sim_matrix,
            "id_to_index": id_to_index,
            "index_to_id": dict(zip(posts_df.index, posts_df['id']))
        }
        
        with open("recommendation_model.pkl", "wb") as f:
            pickle.dump(model_data, f)
            
        print("모델 빌드 및 저장 완료: recommendation_model.pkl")

    except Exception as e:
        print(f"모델 빌드 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    build_recommendation_model()