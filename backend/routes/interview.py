from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Annotated
from question_llm.interview.generate_questions import generate_questions
from question_llm.interview.database_utils import create_new_interview
from models import Interview
from database import SessionLocal
from .crud import get_interviews_by_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import  datetime
from question_llm.interview.database_utils import save_questions_to_db, save_evaluated_answers_to_db
from question_llm.interview.collect_answer import collect_answers
from question_llm.interview.generate_report import generate_report
from question_llm.interview.evaluate_answers import evaluate_answer
from question_llm.interview.evaluate_answer_2nd import evaluate_responses, parse_report
from models import EvaluateAnswersRequest, Interview, QuestionTb, ReportTb
from sentence_transformers import SentenceTransformer
import asyncio
import os
from util.upload_to_s3 import upload_to_s3
from botocore.exceptions import NoCredentialsError
from question_llm.interview.keyword_s3 import keyword_main, ResumePathManager
import json

from fastapi import FastAPI, Form

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

def use_resume_path():

    resume_path = ResumePathManager.get_path()
    return resume_path
    # 추가 작업 수행 가능



def makequestion(user_id, user_job, make_keywords, db_session: Session):  
    """
    모의 면접 프로세스 관리.
    """

    JOB_TALENT = make_keywords
    USER_ID = user_id
    USER_JOB = user_job
    
    keywords = JOB_TALENT.split(", ")
    pdf_path = use_resume_path()

    RESUME_PATH = pdf_path

    try:
        # Step 1: 인터뷰 생성 및 ID 확보
        interview_id = create_new_interview(
            user_id=USER_ID,
            user_job=USER_JOB,
            resume_path=RESUME_PATH,
            db_session=db_session  
        )
        if not interview_id:
            raise ValueError("Failed to create new interview.")
        print(f"Interview created with ID: {interview_id}")

        questions = generate_questions(keywords, interview_id, USER_ID,  db_session)
        
        # save_questions_to_db(interview_id, questions, db_session)
        
        return questions, interview_id
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred during the mock interview process: {e}")
        raise



# S3 관련 설정
S3_BUCKET = "sk-unailit"
file_name = f"resume_{id}.pdf"  # 파일명 동적 생성

@router.post("/generate_question")
def generate_interview_questions(
    user_id: Annotated[int, Form()],
    user_job: Annotated[str, Form()],
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # 파일 확장자 확인
        file_extension = os.path.splitext(resume.filename)[1]
        if file_extension not in ['.pdf']:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF are allowed.")

        # 고유한 파일명 생성
        unique_filename = f"resume/{user_id}/resume_{user_id}.pdf"

        # S3에 파일 업로드
        try:
            s3_path = upload_to_s3(resume.file, S3_BUCKET, unique_filename)
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="Failed to upload file: S3 credentials not available")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
        
        
        make_keywords = keyword_main(user_id)

        # 질문 생성 및 인터뷰 ID 얻기
        questions, interview_id = makequestion(user_id,user_job, make_keywords, db)

        return {
            "message": "Questions generated successfully",
            "interview_id": interview_id,
            "questions": questions,
            "resume_path": s3_path
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/evaluate_answers")
async def evaluate_answers(request: EvaluateAnswersRequest, db: Session = Depends(get_db)):
    # 평가 실행
    ragas_df, total_score, level, summary_resp = evaluate_responses(request.interview_id, request.answers)
    parsed_report = parse_report(summary_resp)

    # 문항별 평가 데이터를 JSON 형식으로 변환
    question_feedback = {
        key: value for key, value in parsed_report.items() if key.startswith("문항")
    }

    # DB에 데이터 저장
    try:
        new_report = ReportTb(
            interview_id=request.interview_id,
            strength=parsed_report.get("강점", ""),
            weakness=parsed_report.get("약점", ""),
            ai_summary=parsed_report.get("한줄평", ""),
            detail_feedback=json.dumps(question_feedback, ensure_ascii=False),  # 문항별 평가 데이터를 JSON 형식으로 저장
            report_score=total_score,
            report_created=datetime.now()  # 현재 로컬 시간 사용
        )
        db.add(new_report)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving report to database: {str(e)}")

    # 결과 반환
    return {
        "summary_resp": summary_resp,
        "parsed_report": parsed_report
    }



@router.get("/interview/{user_id}")
async def read_interviews(user_id: int, db: Session = Depends(get_db)):
    interviews = get_interviews_by_user_id(db=db, user_id=user_id)
    if not interviews:
        raise HTTPException(status_code=404, detail="No interviews found for this user")
    
    return [{"interview_id": interview.interview_id, "interview_created": interview.interview_created} for interview in interviews]



@router.get("/interviews/{interview_id}/questions", response_model=dict)
def get_interview_questions(interview_id: int, db: Session = Depends(get_db)):
    # Interview와 관련된 모든 Question을 조회
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # 관련된 질문 가져오기
    questions = db.query(QuestionTb).filter(QuestionTb.interview_id == interview_id).all()
    
    # 결과 반환
    return {
        "interview_id": interview.interview_id,
        "user_job": interview.user_job,
        "questions": [
            {
                "question_id": q.question_id,
                "job_question_kor": q.job_question_kor,
                "job_answer": q.job_answer_kor,
                "job_solution": q.job_solution_kor,
                "job_score": q.job_score
            } for q in questions
        ]
    }

@router.get("/interviews/{interview_id}/report", response_model=dict)
def get_report(interview_id: int, db: Session = Depends(get_db)):
    # Report 조회
    report = db.query(ReportTb).filter(ReportTb.interview_id == interview_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # 결과 반환
    return {
        "interview_id": report.interview_id,
        "strength": report.strength,
        "weakness": report.weakness,
        "ai_summary": report.ai_summary,
        "detail_feedback": report.detail_feedback,
        "report_score": report.report_score,
        "report_created": report.report_created
    }

