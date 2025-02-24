
import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))

def load_llm_config(secrets_path):
    try:
        with open(secrets_path, 'r') as file:
            llm_config = json.load(file).get("llm", {})
            return llm_config
    except Exception as e:
        print(f"파일({secrets_path}) LLM config 읽기 오류: {e}")
        return {}

secrets_path = os.path.join(project_dir, "secrets.json")
llm_config = load_llm_config(secrets_path)

def set_gemini_model(temperature: float, api_key=None):
    try:
        gemini_config = llm_config.get("gemini", {})
        llm = ChatGoogleGenerativeAI(
            model=gemini_config.get("MODEL_NAME", ""),
            google_api_key=api_key if api_key is not None else gemini_config.get("api_key", {}).get("GOOGLE_API_KEY5", ""),
            temperature=temperature,
        )
    except Exception as e:
        print(f"Gemini model 생성 오류: {e}")
        return None
    
    return llm

def call_LLM(llm, prompt) -> str:
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"LLM 호출 오류: {e}")
        return -1

# 테스트용
if (__name__ == "__main__"):
    # 테스트 1-1: set_gemini_model
    gemini_llm = set_gemini_model(temperature=0.0)
    print(f"gemini: {gemini_llm}")

    # 테스트 1-2: set_chatgpt_model
    # chatgpt_llm = set_chatgpt_model(0.0)
    # print(f"chatgpt: {chatgpt_llm}")

    # 테스트 2: call_llm
    query = """
내일 날씨는 어때?
"""
    gemini_response = call_LLM(gemini_llm, query)
    print(f"gemini response: {gemini_response}")

    print("\n")

    # chatgpt_response = call_LLM(chatgpt_llm, query)       # 과금으로 인한 주석처리, 필요 시 주석 해제 후 간단한 쿼리로 테스트 진행
    # print(f"chatgpt response: {chatgpt_response}")
