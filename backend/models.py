from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Date, Text, DECIMAL
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.orm import configure_mappers
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from pydantic import BaseModel
from datetime import date, datetime
from sqlalchemy.sql import func
from typing import List






class User(Base):
    __tablename__ = "user_tb"  

    id = Column(String(45), primary_key=True, index=True) 
    user_name = Column(String(45))  
    user_email = Column(String(45)) 
    user_joined = Column(Date)  


class UserToken(Base):
    __tablename__ = "token_tb"

    id = Column(String(45), ForeignKey("user_tb.id"), primary_key=True)  
    refresh_token = Column(String(255), nullable=True)
    refresh_token_created = Column(DateTime(timezone=True), server_default=func.now())



class UserRegister(BaseModel):
    name: str
    email: str
    id: int
    user_joined: date

class Interview(Base):
    __tablename__ = "interview_tb"

    interview_id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(String(45), nullable=False)                 
    user_job = Column(String(255), nullable=True)                
    interview_created = Column(DateTime, nullable=False)         
    resume_path = Column(String(255), nullable=True) 

    
class Board(Base):
    __tablename__ = "board_tb"

    idx = Column(Integer, primary_key=True, autoincrement=True)  
    id = Column(String(45), nullable=False)  
    title = Column(String(255), nullable=False)  
    content = Column(String(255), nullable=False)  
    post_date = Column(DateTime, nullable=False, default=func.now())  
    del_yn = Column(String(1), nullable=False, default='Y')






class ReportTb(Base):
    __tablename__ = 'report_tb'

    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    strength = Column(String(255), nullable=False)
    weakness = Column(String(255), nullable=False)
    ai_summary = Column(DateTime, nullable=False)
    detail_feedback = Column(Text, nullable=False)
    report_score = Column(Integer, nullable=False)
    report_created = Column(DateTime, nullable=False)

class QuestionTb(Base):
    __tablename__ = 'question_tb'

    question_id = Column(Integer, primary_key=True)
    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    job_question_kor = Column(String(255), nullable=True)
    job_question_eng = Column(String(255), nullable=True)
    job_answer_kor = Column(String(255), nullable=True)
    job_answer_eng = Column(String(255), nullable=True)
    job_solution_kor = Column(String(255), nullable=True)
    job_solution_eng = Column(String(255), nullable=True)
    job_context = Column(String(255), nullable=True)
    job_score = Column(DECIMAL, nullable=True)
    interview = relationship('Interview')

class Answer(BaseModel):
    interview_id: int
    job_question_kor: str
    job_answer_kor: str
    job_solution_kor: str

class EvaluateAnswersRequest(BaseModel):
    interview_id: int
    answers: List[Answer]
