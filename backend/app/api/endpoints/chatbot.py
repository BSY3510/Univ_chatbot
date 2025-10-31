from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import google.generativeai as genai
from dotenv import load_dotenv
import yaml

from app.db import schemas
from app.db.session import SessionLocal

load_dotenv() 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge_base.pkl")
PROMPT_PATH = os.path.join(BASE_DIR, "app", "core", "prompts.yaml")

EMBEDDING_MODEL_NAME = 'jhgan/ko-sroberta-multitask'

def load_prompt_template(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data["rag_prompt_template"]
    except Exception as e:
        print(f"[치명적 오류] 챗봇 API: 프롬프트 파일({path}) 로드 실패 - {e}")
        return None

try:
    print("챗봇 API: 임베딩 모델 로드 중...")
    embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
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

except Exception as e:
    print(f"[치명적 오류] 챗봇 API: 지식 베이스 로드 실패 - {e}")
    embed_model = None
    index = None
    metadata = []

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
    genai.configure(api_key=GOOGLE_API_KEY)
    
    generation_config = {
        "temperature": 0.7, "top_p": 1, "top_k": 1, "max_output_tokens": 2048,
    }
    
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config
    )
    print("챗봇 API: Gemini 모델 로드 완료.")

    RAG_PROMPT_TEMPLATE = load_prompt_template(PROMPT_PATH)
    if RAG_PROMPT_TEMPLATE is None:
        raise ValueError("프롬프트 템플릿 로드에 실패했습니다.")
    
    print("챗봇 API: 프롬프트 템플릿 로드 완료.")

except Exception as e:
    print(f"[치명적 오류] 챗봇 API: Gemini 또는 프롬프트 로드 실패 - {e}")
    gemini_model = None
    RAG_PROMPT_TEMPLATE = None

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chatbot", response_model=schemas.GeminiChatbotResponse)
def get_chatbot_response(request: schemas.ChatbotRequest):
    """
    사용자의 질문(query)을 받아, RAG 파이프라인을 거쳐
    자연어 답변과 근거 자료를 반환합니다.
    """
    if embed_model is None or index is None or gemini_model is None or RAG_PROMPT_TEMPLATE is None:
        raise HTTPException(status_code=500, detail="챗봇 모델이 로드되지 않았습니다.")

    try:
        query_vector = embed_model.encode([request.query], show_progress_bar=False)
        query_vector_np = np.array(query_vector).astype('float32')

        k = 3
        D, I = index.search(query_vector_np, k)

        retrieved_sources = [] 
        context_str = ""
        
        for i, idx in enumerate(I[0]):
            meta = metadata[idx]
            context_str += f"\n--- 참고 자료 {i+1} (출처 ID: {meta['post_id']}) ---\n"
            context_str += f"제목: {meta['post_title']}\n"
            context_str += f"내용: {meta['text']}\n"
            
            retrieved_sources.append(schemas.ChatbotSource(
                post_id=meta['post_id'],
                post_title=meta['post_title'],
                text=meta['text']
            ))
        
        if not retrieved_sources:
             return schemas.GeminiChatbotResponse(
                answer="죄송합니다. 관련 정보를 찾지 못했습니다.",
                sources=[]
            )

        prompt = RAG_PROMPT_TEMPLATE.format(
            context_str=context_str,
            query=request.query
        )
        
        response = gemini_model.generate_content(prompt)
        gemini_answer = response.text

        return schemas.GeminiChatbotResponse(
            answer=gemini_answer,
            sources=retrieved_sources
        )

    except Exception as e:
        print(f"챗봇 응답 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail="챗봇 응답 생성 중 오류 발생")