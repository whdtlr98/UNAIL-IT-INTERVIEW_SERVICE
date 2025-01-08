import logging
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from datetime import datetime
import os
from .database_utils import save_report_to_db
from util.get_parameter import get_parameter

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import re

openai_api_key = get_parameter('/TEST/CICD/STREAMLIT/OPENAI_API_KEY')
# openai_api_key = os.getenv("OPENAI_API_KEY")


def clean_text(text):
    # 콜론과 그 뒤의 공백 제거
    text = re.sub(r':\s*', '', text)
    # 숫자, 점, 공백으로 시작하는 부분 제거 (예: "1. ")
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    # 줄바꿈 문자를 공백으로 대체
    text = text.replace('\n', ' ')
    # 연속된 공백을 하나의 공백으로 대체
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return text.strip()

def get_client():
    try:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        return ChatOpenAI(
            model="gpt-4o-mini", 
            streaming=True,
            openai_api_key=openai_api_key
        )
    except Exception as e:
        logger.error(f"Error creating ChatOpenAI client: {e}")
        raise

# ChatOpenAI 인스턴스 생성
try:
    chat = get_client()
except Exception as e:
    logger.error(f"Failed to initialize ChatOpenAI client: {e}")
    raise

def generate_report(evaluation_results: List[Dict],interview_id, db_session) -> Dict:
    
    try:
        if not evaluation_results:
            raise ValueError("evaluation_results is empty")

        # 평가 데이터 정리
        detail_feedback = [{"question": result.get("question", ""), "answer": result.get("answer", ""), "feedback": result.get("feedback", "")} for result in evaluation_results]
        average_score = round(sum(result.get("score", 0) for result in evaluation_results) / len(evaluation_results), 2)

        logger.info(f"Processed {len(detail_feedback)} feedback items")

        # GPT 모델 프롬프트 생성
        prompt = (
            "다음은 면접 결과입니다.\n"
            "질문과 피드백을 기반으로 강점, 약점, 한줄평을 작성해 주세요.\n\n"
            "면접 결과:\n"
        )
        for result in evaluation_results:
            prompt += f"질문: {result.get('question', '')}\n답변: {result.get('answer', '')}\n피드백: {result.get('feedback', '')}\n\n"
        prompt += (
            "강점:\n- 주요 강점 3가지를 작성해 주세요.\n\n"
            "약점:\n- 주요 약점 3가지를 작성해 주세요.\n\n"
            "한줄평:\n- 사용자를 위한 한줄평을 작성해 주세요."
        )

        # GPT 모델 요청
        try:
            response = chat.invoke([SystemMessage(content=prompt)])
            feedback = response.content.strip()
            logger.info("Successfully generated feedback from GPT model")
        except Exception as e:
            logger.error(f"Error generating final feedback: {e}")
            feedback = "오류 발생"

        # 보고서 데이터 구성
        try:
            report_data = {
            "interview_id": interview_id,
            "strength": clean_text("강점 없음" if "강점" not in feedback else feedback.split("약점")[0].strip()),
            "weakness": clean_text("약점 없음" if "약점" not in feedback else feedback.split("한줄평")[0].split("약점")[1].strip()),
            "ai_summary": clean_text("한줄평 없음" if "한줄평" not in feedback else feedback.split("한줄평")[1].strip()),
            "report_score": average_score,
            "detail_feedback": str(detail_feedback),
        }

    # 보고서 데이터를 저장
            save_report_to_db(db_session=db_session, **report_data)
            logger.info("Successfully saved report to database")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error saving report to DB: {e}")
            logger.error(f"Report data: {report_data}")
            raise


        return report_data

    except Exception as e:
        logger.error(f"Unexpected error in generate_report: {e}")
        raise