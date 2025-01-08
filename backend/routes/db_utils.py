from sqlalchemy.exc import SQLAlchemyError
import sys
import os
import datetime

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database import SessionLocal
from models import QuestionTb, ReportTb


# 데이터베이스 세션 생성
db_session = SessionLocal()

def save_question_to_db(interview_id, job_question, job_answer, job_solution, job_score, question_vector):
    """
    QuestionTb 테이블에 데이터를 저장합니다.
    """
    try:
        question = QuestionTb(
            interview_id=interview_id,
            job_question_kor=job_question,
            job_answer_kor=job_answer,
            job_solution_kor=job_solution,
            job_score=job_score,
            question_vector_path=question_vector,
        )
        
        db_session.add(question)
        db_session.commit()
        print("Question saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving question to DB: {e}")
    finally:
        db_session.close()


def update_question_in_db(
    question_id: int,
    interview_id: int,
    job_question: str,
    job_answer: str,
    job_solution: str,
    job_answer_score: float
):
    """
    QuestionTb에 데이터를 업데이트하는 함수.
    """
    try:
        question = db_session.query(QuestionTb).filter_by(id=question_id, interview_id=interview_id).first()
        if not question:
            raise ValueError(f"Question with ID {question_id} and interview_id {interview_id} not found.")

        # 필드 업데이트
        question.job_question = job_question
        question.job_answer = job_answer
        question.job_solution = job_solution
        question.job_answer_score = job_answer_score

        db_session.commit()
        print(f"Question {question_id} updated successfully.")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error updating QuestionTb: {e}")
    finally:
        db_session.close()




def save_report_to_db(interview_id, strength, weakness, ai_summary, detail_feedback, attitude, report_score):
    """
    ReportTb 테이블에 데이터를 저장합니다.
    """
    try:
        report = ReportTb(
            interview_id=interview_id,
            strength=strength,
            weakness=weakness,
            ai_summary=ai_summary,
            detail_feedback=detail_feedback,
            report_score=report_score,
        )
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
    finally:
        db_session.close()


def save_report_to_db(
    interview_id: int,
    strength: str,
    weakness: str,
    ai_summary: str,
    detail_feedback: str,
    report_score: int,
):
    """
    ReportTb 테이블에 데이터를 저장합니다.
    """
    try:
        report = ReportTb(
            interview_id=interview_id,
            strength=strength,
            weakness=weakness,
            ai_summary=ai_summary,
            detail_feedback=detail_feedback,
            report_score=report_score,
            report_created=datetime.now(),  # 생성 시간 추가
        )
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
        raise e



