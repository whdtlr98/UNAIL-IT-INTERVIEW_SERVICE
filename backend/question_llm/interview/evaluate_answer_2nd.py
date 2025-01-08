import os
import pandas as pd
import re
from haystack import Pipeline
from haystack_integrations.components.evaluators.ragas import RagasEvaluator, RagasMetric
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from question_llm.interview.database_utils import load_data_by_interview_id, get_job_questions_by_interview_id
from models import Answer
from typing import List, Dict
import openai
import boto3
from langchain.schema import SystemMessage, HumanMessage
from sqlalchemy.orm import Session
from database import SessionLocal

############################################
# 시스템 프롬프트 
############################################
SYSTEM_PROMPT = """
    ### **1. 문제 정의**

    ### 요구사항:

    1. **평가 항목**:
        - **답변 내용 정확성(정량적 점수)**:
          면접자가 질문에 대해 얼마나 정확하고 구체적으로 답변했는지를 평가합니다. 질문과 답변의 관련성을 평가하며, 관련된 경험이나 사례를 구체적으로 제시했는지도 확인합니다.
        - **논리성(STAR 기법)**:
          답변의 논리적 구조를 중점적으로 평가합니다. STAR 기법(Situation, Task, Action, Result)을 기준으로 답변이 체계적으로 구성되었는지, 논리적으로 설득력이 있는지를 확인합니다.
        - **직무적합성**:
          면접자가 답변을 통해 직무에 필요한 핵심 역량과 경험을 보여주는지를 평가합니다. 직무와의 연관성을 바탕으로, 답변이 직무 요구사항과 얼마나 부합하는지를 분석합니다.
    2. **정량적 기준**:
        - **점수 분포: 3~9점 (문항당)**:
          각 문항은 정량적으로 평가되며, 각각 1~3점의 점수가 부여됩니다.(정확성, 직무적합성(및 역량), 논리성)
          합산하여 문항당 총점은 최소 3점, 최대 9점입니다.
        - **총점: 15~45점**:
          총 5개의 문항에 대해 점수를 합산하여 최종 점수를 산출합니다. 총점은 15점(최저)에서 45점(최고) 사이입니다.

    ---

    ### 2. 과정

    ### **Step 1: 답변 내용 정확성 평가**
    (상세 기준 및 예시 포함)

    ### **Step 2: 직무 및 역량 평가**
    - 직무적합성 (1~3점)
    - 문제 해결 능력, 협업 능력, 의사소통 능력, 성장 가능성, 대인 관계 능력 각각 (1~3점)
    - 이들 점수를 합산 후 우수/보통/미흡(3/2/1점) 변환

    ### **Step 3: 논리성 평가 (STAR 기법)**
    (1~3점)

    ### **Step 4: 최종 보고서 산출**
    - 문항별 점수와 이유를 바탕으로 강점, 약점, 한줄평, 결과단계를 자세히 기술
"""




def fetch_openai_api_key(parameter_name="/TEST/CICD/STREAMLIT/OPENAI_API_KEY"):
    try:
        ssm_client = boto3.client("ssm", region_name="ap-northeast-2")
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        api_key = response["Parameter"]["Value"]
        os.environ["OPENAI_API_KEY"] = api_key
        return api_key
    except Exception as e:
        raise RuntimeError(f"Error fetching parameter: {str(e)}")

# Fetch and set the API key
openai_api_key = os.environ.get("OPENAI_API_KEY") or fetch_openai_api_key()

############################################
# 데이터 로드 및 RAGAS 평가 함수
############################################
# def load_data(file_path: str):
#     get_job_questions_by_interview_id
#     data = pd.read_csv(file_path)
#     questions = data['job_question_english'].tolist()
#     contexts = [[str(context)] for context in data['job_context']]
#     responses = data['response_eng'].tolist()
#     ground_truths = data['job_solution_english'].tolist()
#     return questions, contexts, responses, ground_truths

def run_ragas_evaluation(questions, contexts, responses, ground_truths):
    answer_relevancy_pipeline = Pipeline()
    evaluator_relevancy = RagasEvaluator(
        metric=RagasMetric.ANSWER_RELEVANCY,
        metric_params={"strictness": 2}
    )
    answer_relevancy_pipeline.add_component("evaluator", evaluator_relevancy)

    answer_correctness_pipeline = Pipeline()
    evaluator_correctness = RagasEvaluator(
        metric=RagasMetric.ANSWER_CORRECTNESS,
        metric_params={"weights": [0.5, 0.2]}
    )
    answer_correctness_pipeline.add_component("evaluator", evaluator_correctness)

    relevancy_raw = answer_relevancy_pipeline.run(
        {"evaluator": {"questions": questions, "contexts": contexts, "responses": responses}}
    )["evaluator"]["results"]

    correctness_raw = answer_correctness_pipeline.run(
        {"evaluator": {"questions": questions, "responses": responses, "ground_truths": ground_truths}}
    )["evaluator"]["results"]

    answer_relevancy_scores = []
    for result in relevancy_raw:
        for metric in result:
            if metric['name'] == 'answer_relevancy':
                answer_relevancy_scores.append(metric['score'])
                break

    answer_correctness_scores = []
    for result in correctness_raw:
        for metric in result:
            if metric['name'] == 'answer_correctness':
                answer_correctness_scores.append(metric['score'])
                break

    df = pd.DataFrame({
        'answer_relevancy': answer_relevancy_scores,
        'answer_correctness': answer_correctness_scores
    })
    df['average_score'] = df[['answer_relevancy', 'answer_correctness']].mean(axis=1)
    return df

def step1_rating(score: float) -> str:
    if score >= 0.5:
        return "우수"
    elif score >= 0.3:
        return "보통"
    else:
        return "미흡"

def parse_jobfit_output(text: str) -> int:
    matches = re.findall(r"\((\d)점\)", text)
    if matches:
        scores = list(map(int, matches))
        return round(sum(scores)/len(scores))
    return 2

def parse_logic_output(text: str) -> int:
    match = re.search(r"\((\d)점\)", text)
    if match:
        return int(match.group(1))
    return 2

def calc_final_scores(evaluation_df):
    rating_to_score = {"우수": 3, "보통": 2, "미흡": 1}
    evaluation_df['step1_score'] = evaluation_df['step1_rating'].map(rating_to_score)
    evaluation_df['total_question_score'] = evaluation_df['step1_score'] + evaluation_df['job_fit_score'] + evaluation_df['logic_score']
    total_score = evaluation_df['total_question_score'].sum()

    if 15 <= total_score <= 20:
        level = "매우 미흡"
    elif 21 <= total_score <= 26:
        level = "미흡"
    elif 27 <= total_score <= 32:
        level = "보통"
    elif 33 <= total_score <= 38:
        level = "우수"
    elif 39 <= total_score <= 45:
        level = "매우 우수"
    else:
        level = "알 수 없음"

    return evaluation_df, total_score, level

############################################
# 스텝별 프롬프트 정의
############################################

step1_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(
        """
위 시스템 프롬프트의 Step 1 기준에 따라 아래 질문과 답변의 정확성을 평가하고, 우수/보통/미흡(3/2/1점) 판정과 근거를 아주 상세하고 세세하게 제시하세요.
질문: {question}
답변: {answer}
Answer Relevancy: {answer_relevancy}
Answer Correctness: {answer_correctness}
"""
    )
])

step2_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(
        """
위 시스템 프롬프트의 Step 2 기준에 따라 아래 질문과 답변을 평가하고, 직무적합성 및 각 소프트스킬 점수를 (1~3점) 부여 후 우수/보통/미흡(3/2/1점)으로 환산하고, 그 근거를 매우 상세히 제시하세요.
질문: {question}
답변: {answer}
"""
    )
])

step3_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(
        """
위 시스템 프롬프트의 Step 3 기준에 따라 아래 질문과 답변을 STAR 기법으로 분석하고, 우수/보통/미흡(3/2/1점) 판정 및 근거를 매우 상세히 제시하세요.
질문: {question}
답변: {answer}
"""
    )
])

def create_df_summary(evaluation_df):
    summary_lines = []
    for i, row in evaluation_df.iterrows():
        summary_lines.append(
            f"문항 {i+1}:\n"
            f"- 정확성: {row['step1_score']}점\n"
            f"- 직무적합성+역량(스텝2): {row['job_fit_score']}점\n"
            f"- 논리성(스텝3): {row['logic_score']}점\n"
            f"- 총점: {row['total_question_score']}점\n"
            f"직무적합성 평가 내용:\n{row['jobfit_score_description']}\n"
            f"논리성 평가 내용:\n{row['logic_scores_description']}\n"
        )
    return "\n".join(summary_lines)

step4_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(
        """
이미 문항별 점수와 이유가 결정된 상태입니다.
아래는 문항별 세부 결과 요약입니다:

{df_summary}

총점: {total_score}, 평가 단계: {level}

위 시스템 프롬프트의 Step 4 기준에 따라,
- 문항별 세부 평가(2~3줄 이유 포함)
- 종합 평가(강점, 약점, 한줄평, 결과단계)
를 텍스트 형식으로 매우 상세하고 세세하게 제시하세요. 마크다운 언어는 사용하지 마세요.
"""
    )
])

def parse_report(summary_text: str) -> dict:
    # 정규식 패턴 정의
    question_pattern = re.compile(r'문항 (\d+):([\s\S]*?)(?=\n문항 \d+:|종합 평가:)', re.DOTALL)
    item_pattern = re.compile(r'- (\w+(?:\+\w+)?): (\d+)점\. (.+)')
    strength_pattern = re.compile(r'강점: (.+?)(?=\n약점:|$)', re.DOTALL)
    weakness_pattern = re.compile(r'약점: (.+?)(?=\n한줄평:|$)', re.DOTALL)
    short_eval_pattern = re.compile(r'한줄평: (.+?)(?=\n결과단계:|$)', re.DOTALL)
    result_pattern = re.compile(r'결과단계: (.+)', re.DOTALL)

    # 결과 저장용 dict
    report = {}

    # 문항별 세부 평가 추출
    questions = question_pattern.findall(summary_text)
    for q_num, q_text in questions:
        q_dict = {}
        items = item_pattern.findall(q_text)
        for category, score, desc in items:
            # category를 변환해 직무적합성_역량 등 사용
            if category == "직무적합성+역량":
                category = "직무적합성_역량"
            q_dict[category] = {
                "score": int(score),
                "description": desc.strip()
            }
        report[f"문항{q_num}"] = q_dict

    # 종합 평가 항목 추출
    strength = strength_pattern.search(summary_text)
    weakness = weakness_pattern.search(summary_text)
    short_eval = short_eval_pattern.search(summary_text)
    result = result_pattern.search(summary_text)

    if strength:
        report["강점"] = strength.group(1).strip()
    if weakness:
        report["약점"] = weakness.group(1).strip()
    if short_eval:
        report["한줄평"] = short_eval.group(1).strip()
    if result:
        report["결과단계"] = result.group(1).strip()

    return report


def get_client():
    return ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        openai_api_key=openai_api_key
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()



def translate_korean_answers_to_english(answers):
    """
    Translates an array of Korean answers into English.
    """
    translated_answers = []
    
    for answer in answers:
        translation_prompt = (
            f"Translate the following text into English:\n\n"
            f"Answer:\n{answer}\n"
        )

        try:
            response = chat.invoke([
                SystemMessage(content="You are a professional translator."),
                HumanMessage(content=translation_prompt)
            ])
            translated_answer = response.content.strip()
            translated_answers.append(translated_answer)
        except Exception as e:
            print(f"An error occurred during translation for answer: {answer}. Error: {str(e)}")
            translated_answers.append(None)

    return translated_answers

############################################
# 실행
############################################

def save_answers_to_db(session: Session, interview_id: int, answers: List[Answer]):
    # 인터뷰 ID에 해당하는 질문 가져오기
    questions = get_job_questions_by_interview_id(session, interview_id)

    responses = [answer.job_answer_kor for answer in answers]
    responses_eng = translate_korean_answers_to_english(responses)  # 한글 답변을 영어로 번역

    for index, question in enumerate(questions):
        # 한글 답변과 영어 번역된 답변을 가져오기
        korean_answer = responses[index] if index < len(responses) else ""
        english_answer = responses_eng[index] if index < len(responses_eng) else ""
        
        # 해당 질문에 대한 답변 업데이트
        question.job_answer_kor = korean_answer
        question.job_answer_eng = english_answer
        
        # DB에 커밋하여 저장
        session.commit()


def evaluate_responses(interview_id,  answers: List[Answer]):
    # 데이터 로드
    session: Session = SessionLocal()

    print("interviewId_response:")
    job_questions, job_contexts, responses, job_solutions = load_data_by_interview_id(interview_id, answers)


    responses_eng = translate_korean_answers_to_english(responses)
    
    save_answers_to_db(session, interview_id, answers)


    # RAGAS 평가
    ragas_df = run_ragas_evaluation(job_questions, job_contexts, responses_eng, job_solutions)
    ragas_df['step1_rating'] = ragas_df['average_score'].apply(step1_rating)

    # 새로운 컬럼 초기화
    ragas_df['job_fit_score'] = 0
    ragas_df['logic_score'] = 0
    ragas_df['jobfit_score_description'] = ""
    ragas_df['logic_scores_description'] = ""

    # LLM 세팅
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

    step1_chain = LLMChain(llm=llm, prompt=step1_prompt)
    step2_chain = LLMChain(llm=llm, prompt=step2_prompt)
    step3_chain = LLMChain(llm=llm, prompt=step3_prompt)
    step4_chain = LLMChain(llm=llm, prompt=step4_prompt)

    # 모든 문항 평가
    for i, (q, ans) in enumerate(zip(job_questions, responses)):
        answer_relevancy = ragas_df['answer_relevancy'][i]
        answer_correctness = ragas_df['answer_correctness'][i]

        # Step 1
        step1_resp = step1_chain.run(question=q, answer=ans, answer_relevancy=answer_relevancy, answer_correctness=answer_correctness)

        # Step 2
        step2_resp = step2_chain.run(question=q, answer=ans)
        jf_score = parse_jobfit_output(step2_resp)
        ragas_df.loc[i, 'job_fit_score'] = jf_score
        ragas_df.loc[i, 'jobfit_score_description'] = step2_resp

        # Step 3
        step3_resp = step3_chain.run(question=q, answer=ans)
        lg_score = parse_logic_output(step3_resp)
        ragas_df.loc[i, 'logic_score'] = lg_score
        ragas_df.loc[i, 'logic_scores_description'] = step3_resp

    # 최종 점수 계산
    ragas_df, total_score, level = calc_final_scores(ragas_df)

    # Step 4: 최종 요약 생성
    df_summary = create_df_summary(ragas_df)
    summary_resp = step4_chain.run(
        df_summary=df_summary,
        total_score=str(total_score),
        level=level
    )
    print('summary')
    print(summary_resp)

    return ragas_df, total_score, level, summary_resp

def main():
    file_path = ""
    ragas_df, total_score, level, summary_resp = evaluate_responses(file_path)
    parsed_report = parse_report(summary_resp)

if __name__ == "__main__":
    main()

