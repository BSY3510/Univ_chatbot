from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import posts, chatbot

app = FastAPI(title="Univ_Chatbot API")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/api")

app.include_router(chatbot.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Univ_Chatbot API에 오신 것을 환영합니다!"}