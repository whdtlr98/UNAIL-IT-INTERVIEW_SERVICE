import pandas as pd
from typing import Dict, List, Tuple
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.dialects.mysql import insert 
from database import SessionLocal
from models import QuestionTb, ReportTb, Interview

def update_question_in_db(
    question_id: int,
    interview_id: int,
    job_question: str,
    job_answer: str,
    job_solution: str,
    job_score: float,
) -> bool:

    # DB 세션 생성
    session: Session = SessionLocal()
    try:
        # 업데이트할 질문 가져오기
        question = session.query(QuestionTb).filter(QuestionTb.question_id == question_id).first()
        if not question:
            print(f"[DB 오류] question_id={question_id}가 존재하지 않습니다.")
            return False

        # 질문 업데이트
        question.interview_id = interview_id
        question.job_question_kor = job_question
        question.job_answer_kor = job_answer
        question.job_solution_kor = job_solution
        question.job_score = job_score

        # 변경 사항 커밋
        session.commit()
        print(f"[DB 업데이트 성공] question_id={question_id}, interview_id={interview_id}")
        return True

    except Exception as e:
        session.rollback()  # 트랜잭션 롤백
        print(f"[DB 업데이트 오류] question_id={question_id}, Error: {e}")
        return False

    finally:
        session.close()  # 세션 닫기


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def save_questions_to_db(interview_id: int, questions: List[Dict], db_session):
    for question in questions:
        question_entry = QuestionTb(
            interview_id=interview_id,
            job_question_kor=question["job_question_kor"],
            job_question_eng=question['job_question_eng'],
            job_answer_kor=question["job_answer_kor"],
            job_answer_eng=question['job_answer_eng'],
            job_solution_kor=question["job_solution_kor"],
            job_solution_eng=question['job_solution_eng'],
            job_context=question['job_context'],
            job_score=question["job_score"],
            
        )
        db_session.add(question_entry)
        db_session.commit()


def save_report_to_db(db_session, **kwargs):

    try:
        # ReportTb의 컬럼과 매칭되는 데이터만 필터링
        filtered_data = {key: value for key, value in kwargs.items() if hasattr(ReportTb, key)}
        report = ReportTb(**filtered_data)
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully in DB.")
    except Exception as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
        raise



def create_new_interview(user_id: int, user_job: str, resume_path: str, db_session: Session) -> int:

    try:
        # 인터뷰 데이터 생성
        new_interview = Interview(
            user_id=user_id,
            user_job=user_job,
            resume_path=resume_path,
            interview_created=datetime.now(),
        )

        # DB 세션을 사용하여 데이터 추가 및 커밋
        db_session.add(new_interview)
        db_session.commit()
        db_session.refresh(new_interview)

        # 생성된 인터뷰 ID 반환
        return new_interview.interview_id
    except Exception as e:
        print(f"Error creating interview: {e}")
        db_session.rollback()  # 에러 발생 시 롤백
        return None
    

def create_new_question_in_db(
    interview_id: int,
    job_question_kor: str,
    job_solution_kor: str,
    job_question_eng: str = None,
    job_solution_eng: str = None,
) -> int:
    """
    새로운 질문을 데이터베이스에 추가하고, 생성된 question_id를 반환합니다.
    """
    session: Session = SessionLocal()
    try:
        # 새로운 질문 생성
        new_question = QuestionTb(
            interview_id=interview_id,
            job_question_kor=job_question_kor,
            job_solution_kor=job_solution_kor,
            job_question_eng=job_question_eng,
            job_solution_eng=job_solution_eng,
            job_answer_kor="",  # 기본값 설정
            job_answer_eng="",  # 기본값 설정
            job_score=0.0,  # 초기 점수
            job_context="Default job_context",  # 기본 컨텍스트
        )
        session.add(new_question)
        session.commit()

        # 생성된 question_id 반환
        return new_question.question_id
    except Exception as e:
        session.rollback()
        print(f"[DB 오류] 새로운 질문 생성 실패: {e}")
        return -1  # 실패 시 -1 반환
    finally:
        session.close()
    
def save_answers_to_db(answers: List[Dict]):

    with SessionLocal() as session:
        for answer in answers:
            db_record = QuestionTb(
                question_id=answer["question_id"],
                job_question_kor=answer["question"],
                job_answer_kor=answer["answer"],
                job_solution_kor=answer["ideal_answer"],
                job_score=0,  # 초기 점수 설정
                question_vector_path="default/path/vector.json",
            )
            session.add(db_record)
        session.commit()
    print("Answers successfully saved to the database.")


def save_evaluated_answers_to_db(
    evaluated_answers: List[Dict],
    db_session: Session,
):

    try:
        for answer in evaluated_answers:
            stmt = update(QuestionTb).where(
                QuestionTb.question_id == answer["question_id"]
            ).values(
                interview_id = answer["interview_id"],
                question_id = answer["question_id"],
                job_answer_kor=answer["job_answer_kor"],
                job_answer_eng=answer["job_answer_eng"],
                job_score=answer["job_score"],
                job_context=answer["job_context"],
            )
            db_session.execute(stmt)
        
        db_session.commit()
        print("Evaluated answers updated in DB successfully.")
    except Exception as e:
        db_session.rollback()
        print(f"Error during DB update: {e}")
        raise

def save_report_to_db(
    interview_id: int,
    strength: str,
    weakness: str,
    ai_summary: str,
    detail_feedback: str,
    report_score: int,
    db_session: Session
):

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
    


def get_job_questions_by_interview_id(db: Session, interview_id: int):

    return (
        db.query(QuestionTb)
        .join(Interview, QuestionTb.interview_id == Interview.interview_id)
        .filter(Interview.interview_id == interview_id)
        .all()
    )

def load_data_by_interview_id(interview_id: int, answers) -> Tuple[List[str], List[List[str]], List[str], List[str]]:
    session: Session = SessionLocal()

    # 질문 가져오기
    questions = get_job_questions_by_interview_id(session, interview_id)


    # 결과를 저장할 리스트 초기화
    job_questions = []
    job_contexts = []
    responses = []
    job_solutions = []

    # questions와 answers를 매핑하여 처리
    for index, question in enumerate(questions):  # enumerate를 사용해 인덱스를 추가
        job_questions.append(question.job_question_eng)  # 질문 영어
        job_contexts.append([str(question.job_context)])  # 질문 컨텍스트
        print(f"Number of questions: {len(questions)}")
        print(f"Number of answers: {len(answers)}")

        # answers와 인덱스 매핑
        if index < len(answers):
            responses.append(answers[index].job_answer_kor)  # 사용자의 답변
            job_solutions.append(answers[index].job_solution_kor)  # 정답
        else:
            # answers가 부족할 경우 처리
            responses.append("")  # 빈 값으로 추가
            job_solutions.append("")  # 빈 값으로 추가

    return job_questions, job_contexts, responses, job_solutions


