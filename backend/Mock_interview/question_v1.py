# 필요기능(함수)
# 앱1 = 사용자 데이터 입력 (이력서(경력중심), 프로젝트(내용) => 우리가 기본 포맷을 제공하는게 좋을듯)    
#     = 핵심키워드 추출 (context에 전달할 핵심 정보만 추출) + 직무에 따라 중요한 정보의 가중치를 설정(기술 스택 등)

# 앱2 = 질문생성(RAG) 사용자데이터에서 핵심키워드를 추출 / 프로젝트(자소서)등에서 중요 내용 추출 (gpt) => system prompt 조정  *문장 확인 후 필요시 문장 수정 모델 추가
#     = 1차 질문 답변 이후 사용자 답변 데이터와 사용자데이터 추가 후 추가 질문생성  *질문생성 퀄리티에 따라 생성 추가 요건 부여 
# 공통질문 1 기술질문 2 프젝질문 3

# input1 = technology_context(사용자) => prompt 
#
# input2 = open ai + project_context_summary_command(프로젝트 컨텐츠 요약) 
#
# input3 = *separation - google-STT(질문에 대한 답변)

# technology question = open ai + input1 + prompt (난이도 나누는 함수 필요)
# project question = open ai + input2 + prompt (난이도 나누는 함수 필요)

# 신입, 경력, 박사급 난이도 나눠주세요

# rag쓰자 벡터 db에는 공식홈페이지 논문자료 다 긁어모으고 레그 기반으로 질문생성하자 
# 질문생성과 평가 기준에는 근거자료가 필요한데 지금 모델은 결국 근거가 gpt가 되는 셈이니 근거자료 찾는 것이 중요하다
import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from audio import real_time_transcription  # 실시간 음성 인식 함수가 포함된 모듈

# 환경 변수 로드
load_dotenv()

# ChatOpenAI 클라이언트 생성 함수
def get_client():
    return ChatOpenAI(
        model="gpt-4",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

# ChatOpenAI 인스턴스 생성
chat = get_client()

# 면접 시스템 클래스 정의
class InterviewSystem:
    def __init__(self, gpt_model="gpt-4"):
        self.model = gpt_model
        self.interviewer_prompt = (
            "당신은 현재 지원자를 평가하는 면접관입니다. "
            "지원자의 자기소개서와 기술 스택을 기반으로 질문을 하나만 생성하세요. "
            "하나의 질문만 반환해주시기 바랍니다."
        )
    
    def generate_interview_question(
        self,
        resume_info: str,
        skillset: List[str],
        response_history: List[Dict[str, str]],
        difficulty_level: str = "medium"
    ) -> str:
        # 난이도별 질문 세부 설정
        difficulty_prompt = {
            "low": "기초 수준의 개념을 확인하는 질문을 하나 생성하세요.",
            "medium": "중급 수준의 개념과 문제 해결 능력을 확인하는 질문을 하나 생성하세요.",
            "high": "심도 있는 지식을 평가하는 고급 수준의 질문을 하나 생성하세요."
        }
        
        # 프롬프트 구성
        prompt = (
            f"{self.interviewer_prompt}\n\n"
            f"지원자의 자기소개서 정보: {resume_info}\n"
            f"지원자의 기술 스택: {', '.join(skillset)}\n\n"
            f"{difficulty_prompt.get(difficulty_level, difficulty_prompt['medium'])}\n\n"
        )
        
        # 면접자의 이전 답변이 있는 경우 추가
        if response_history:
            for idx, response in enumerate(response_history, 1):
                prompt += f"{idx}. 질문: {response['question']}\n   답변: {response['answer']}\n\n"
        
        prompt += "다음 질문을 하나만 생성하세요."
        
        # GPT 모델 호출
        response = chat.invoke([
            SystemMessage(content=prompt)
        ])
        
        # 면접 질문 생성 결과 반환
        question = response.content.strip()
        return question

    def generate_feedback(self, response_history: List[Dict[str, str]]) -> str:
        # 피드백 생성을 위한 프롬프트 구성
        prompt = (
            "지원자의 답변 히스토리를 바탕으로 피드백을 작성해주세요. "
            "각 답변의 강점과 개선이 필요한 부분을 간단히 언급해주시고, "
            "지원자의 전체적인 능력을 평가해주세요.\n\n"
            "답변 히스토리:\n"
        )
        
        for idx, response in enumerate(response_history, 1):
            prompt += f"{idx}. 질문: {response['question']}\n   답변: {response['answer']}\n\n"
        
        # GPT 모델 호출로 피드백 생성
        response = chat.invoke([
            SystemMessage(content=prompt)
        ])
        
        feedback = response.content.strip()
        return feedback

# 인터뷰 진행 함수 정의
def conduct_interview(interview_system, resume_info, skillset):
    max_questions = 5
    response_history = []

    for i in range(max_questions):
        # 질문 생성
        question = interview_system.generate_interview_question(
            resume_info=resume_info,
            skillset=skillset,
            response_history=response_history,
            difficulty_level="low"
        )

        # 질문 출력
        print(f"질문 {i + 1}: {question}")

        # 실시간 답변 받기
        final_transcription = real_time_transcription()  # 질문 후에 음성 인식 함수 호출
        
        # 답변 출력
        print(f"답변 {i + 1}: {final_transcription}")
        
        # 질문과 답변을 히스토리에 추가
        response_history.append({"question": question, "answer": final_transcription})
    
    print("인터뷰 종료. 5번의 질문과 답변이 완료되었습니다.")
    
    # 5개의 질문과 답변을 바탕으로 피드백 생성
    feedback = interview_system.generate_feedback(response_history)
    print("피드백:", feedback)
    return response_history, feedback

# 면접 정보 설정 및 인터뷰 실행
resume_info = """농협은행은 고객 중심의 가치를 바탕으로 NH올원뱅크 앱의 편의성을 강화하여 편리한 서비스를 제공하고 있습니다. 
                또한 금융, 생활, 인증을 한 곳에 모은 슈퍼플랫폼으로 도약하는 것이 타 시중은행에 비해 차별화된 경쟁력이라고 생각합니다 
                저는 NH올원뱅크의 서비스 중에서도 고객과의 상호작용을 담당하는 AI톡의 역할이 매우 중요하다고 생각합니다. 
                특히, 고령층 고객이 쉽게 이용할 수 있도록 자연스럽고 직관적인 대화형 AI톡으로 강화될 때 농협은행의 경쟁력을 한층 더 강화할 수 있다고 생각합니다.
                저는 LLaMA등을 활용하여 AI 챗봇을 개발한 경험이 있습니다. 이 과정에서 가장 큰 고충은 한국어의 언어적 특수성을 다루는 것이었습니다. 
                한국어는 어순이 자유롭고, 어미 변화와 존댓말 등의 복잡한 언어적 특징을 가지기 때문에, 답변의 일관성이 떨어지고 정확도가 낮아지는 문제가 발생했습니다. 
                이를 해결하기 위해 LaMA 모델을 한국어 특화 데이터로 fine tuning하여, 챗봇의 텍스트 생성 능력을 높였습니다. 
                최종적으로, 다양한 고객 데이터를 바탕으로 챗봇의 응답이 정확해지도록 많은 테스트를 거쳤습니다. 
                이러한 경험을 바탕으로 NH농협은행의 AI톡 기능을 더욱 강화하여, 고객 맞춤형 서비스를 제공하고 농협은행의 경쟁력을 높이는 데 기여하겠습니다."""

skillset = ["python"]

# InterviewSystem 인스턴스 생성
interview_system = InterviewSystem()

# 인터뷰 시작
interview_log, feedback = conduct_interview(interview_system, resume_info, skillset)
