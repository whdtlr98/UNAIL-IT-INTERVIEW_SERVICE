from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from .prompt import evaluation_prompt
import os
from typing import Dict

# SentenceTransformer 모델 초기화
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# GPT-4 기반 ChatOpenAI 클라이언트 생성 함수
def get_client():
    return ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

# ChatOpenAI 인스턴스 생성
chat = get_client()

# 평가 함수
def evaluate_answer(interview_id, question_id, question, answer, model_answer, model, job_context) -> Dict:

    # 무응답 처리
    if not answer:
        return {
            "interview_id": interview_id,
            "question_id": question_id,
            "job_answer_kor": "None",
            "job_answer_eng": "None",
            "job_score": 0.0,
            "job_context": "No response provided",
        }

    # 코사인 유사도 계산
    answer_embedding = model.encode(answer)
    model_answer_embedding = model.encode(model_answer)
    cosine_sim = cosine_similarity([answer_embedding], [model_answer_embedding])[0][0]
    score = round(cosine_sim * 100, 2)  # 점수를 0~100으로 변환

    # # GPT-4를 사용하여 피드백 생성
    # feedback_prompt = evaluation_prompt(answer, model_answer)
    # feedback_response = chat.invoke([SystemMessage(content=feedback_prompt)])
    # feedback_full = feedback_response.content.strip()

    # # 피드백 추출
    # feedback = ""
    # for line in feedback_full.splitlines():
    #     if line.startswith("피드백"):
    #         feedback = line.replace("피드백:", "", 1).strip()
    #         break

    # if not feedback:
    #     feedback = "No detailed feedback provided."

    # 평가 결과 반환
    return {
        "interview_id":interview_id,
        "question_id": question_id,
        "job_answer_kor": answer,
        "job_answer_eng": translate_to_english(answer, chat),  # 한글 답변을 영어로 번역
        "job_score": score,
        "job_context": job_context,
    }


# 번역 함수
def translate_to_english(korean_text: str, chat) -> str:
    """
    한국어 텍스트를 영어로 번역합니다.
    """
    translation_prompt = f"Translate the following text to English:\n\n{korean_text}"
    try:
        response = chat.invoke([SystemMessage(content=translation_prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation Error"



