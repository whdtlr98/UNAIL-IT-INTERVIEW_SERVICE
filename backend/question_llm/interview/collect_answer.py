from typing import Dict, List
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.schema import SystemMessage
import logging

load_dotenv()


def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()

# GPT 기반 번역 함수
def translate_to_english(korean_text: str, chat) -> str:
    translation_prompt = f"Translate the following text to English:\n\n{korean_text}"
    try:
        response = chat.invoke([SystemMessage(content=translation_prompt)])
        return response.content.strip()
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "Translation Error"

# 질의응답 매핑 함수
def collect_answers(
    answers_from_frontend: List[Dict],
    questions: List[Dict],
) -> List[Dict]:

    print(f"answers_from_frontend: {answers_from_frontend}")
    print(f"questions: {questions}")

    if not isinstance(answers_from_frontend, list):
        raise ValueError("answers_from_frontend must be a list of dictionaries.")

    if not all(isinstance(q, dict) for q in questions):
        raise ValueError("questions must be a list of dictionaries.")

    mapped_answers = []

    for question in questions:
        # 질문 및 이상적 답변
        korean_question = question.get("job_question_kor", "Unknown question")
        english_question = question.get("job_question_eng", "Unknown question")
        model_answer_kor = question.get("job_solution_kor", "No ideal answer provided")
        model_answer_eng = question.get("job_solution_eng", "No ideal answer provided")
        interview_id = question.get("interview_id", 00)
        question_id = question.get("question", 00)
        job_context = question.get("job_context", "None_context")

        # 프론트엔드에서 전달된 답변 매핑
        korean_answer = next(
            (a["answer"] for a in answers_from_frontend if a.get("question") == korean_question),
            None
        )

        # 답변이 없을 경우 샘플 답변 생성
        if not korean_answer:
            print(f"Warning: No answer found for question: {korean_question}. Generating sample answer.")
            korean_answer = f"Sample answer for question: {korean_question[:30]}..."

        # GPT를 사용하여 한글 답변을 영어로 번역
        english_answer = translate_to_english(korean_answer, chat)

        # 매핑된 데이터 저장
        mapped_data = {
            "interview_id": interview_id,
            "question_id":question_id,
            "job_question_kor": korean_question,
            "job_answer_kor": korean_answer,
            "job_solution_kor": model_answer_kor,
            "job_question_eng": english_question,
            "job_answer_eng": english_answer,
            "job_solution_eng": model_answer_eng,
            "job_score": 0,  # 기본 점수 설정
            "job_context": job_context,  # 컨텍스트 추가 가능
        }
        mapped_answers.append(mapped_data)

    print("Answers successfully mapped (DB storage deferred).")
    return mapped_answers
