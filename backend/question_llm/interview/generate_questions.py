import random
import pandas as pd
from typing import List, Dict
import time
from .prompt import question_prompt, model_answer
from datetime import datetime
from langchain_openai import ChatOpenAI
from .database_utils import create_new_question_in_db
from .question_similarity import question_similarity_main
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import uuid 
from util.get_parameter import get_parameter
import boto3
import random

load_dotenv()



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

def get_client():
    return ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        openai_api_key=openai_api_key
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)


# 현재 파일의 디렉토리 경로를 가져옴
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리로 이동 (필요한 만큼 반복).
parent_dir = os.path.dirname(current_dir)

vector_db_high = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "high_db"),
    index_name="python_high_chunk700",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

vector_db_low = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "low_local_db"),
    index_name="python_new_low_chunk700",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)




# 검색기 함수
def cross_encoder_reranker(query, db_level="low", top_k=10):


    # DB 선택
    vector_db = vector_db_high if db_level == "high" else vector_db_low

    # Retriever 설정
    retriever = vector_db.as_retriever()

    # MultiQueryRetriever 생성
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)

    # Cross Encoder Reranker 초기화
    model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
    reranker = CrossEncoderReranker(model=model, top_n=top_k)
    # ContextualCompressionRetriever 생성
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=multi_query_retriever
    )
    # 쿼리에 대한 문서 검색 및 압축
    result_string = " ".join(query)
    compressed_docs = compression_retriever.invoke(result_string)
    

    return compressed_docs



from typing import List
import random
from langchain.schema import SystemMessage

def generate_questions(keywords: List[str], interview_id: int, USER_ID: int, db_session):
    questions = []
    total_questions = 5  # 목표 질문 수

    def add_question(korean_job_question, korean_job_solution, retrieved_content="", selected_keyword=""):
        translation_prompt = (
            f"Translate the following question and its answer into English:\n\n"
            f"Question:\n{korean_job_question}\n\n"
            f"Answer:\n{korean_job_solution}\n"
        )
        try:
            translation_response = chat.invoke([SystemMessage(content=translation_prompt)])
            translated_text = translation_response.content.strip()
            english_job_question, english_job_solution = translated_text.split("\nAnswer:")
        except Exception as e:
            print(f"Error during translation: {e}")
            english_job_question = "Translation Error"
            english_job_solution = "Translation Error"
        
        question_id = create_new_question_in_db(
            interview_id=interview_id,
            job_question_kor=korean_job_question.strip(),
            job_solution_kor=korean_job_solution.strip(),
            job_question_eng=english_job_question.strip(),
            job_solution_eng=english_job_solution.strip(),
        )

        questions.append({
            "question_id": question_id,
            "interview_id": interview_id,
            "job_question_kor": korean_job_question.strip(),
            "job_question_eng": english_job_question.strip(),
            "job_answer_kor": "",
            "job_answer_eng": "",
            "job_solution_kor": korean_job_solution.strip(),
            "job_solution_eng": english_job_solution.strip(),
            "job_context": retrieved_content,
            "job_score": 0,
            "question_vector_path": "default/path/vector.json",
            "selected_keyword": selected_keyword,
        })

    if not keywords:  # 키워드가 없는 경우
        for i in range(total_questions):
            korean_job_question, korean_job_solution = question_similarity_main(i + 1, USER_ID)
            add_question(korean_job_question, korean_job_solution)
            if len(questions) >= total_questions:
                break
    else:
        db_allocation = ["low"] * 5 + ["high"] * 0
        random.shuffle(db_allocation)

        selected_keywords = random.sample(keywords, min(len(keywords), 15))
        combined_keywords = ", ".join(selected_keywords)
        print(f"Combined Keywords: {combined_keywords}")

        for db_level in db_allocation:
            if len(questions) >= total_questions:
                break

            search_results = cross_encoder_reranker(query=combined_keywords, db_level=db_level, top_k=10)
            if not search_results:
                alternate_level = "high" if db_level == "low" else "low"
                search_results = cross_encoder_reranker(query=combined_keywords, db_level=alternate_level, top_k=10)

            if not search_results:
                print("검색 결과가 없습니다.")
                continue

            search_results = random.sample(search_results, min(len(search_results), 5))
            
            for doc in search_results:
                if len(questions) >= total_questions:
                    break

                retrieved_content = doc.page_content

                prompt = question_prompt() + (
                    f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
                    f"다음의 키워드가 공식문서의 데이터와 연관이 있다면 키워드와 공식문서를 함께 활용해서 다채로운 질문을 생성해주세요:\n{combined_keywords}\n"
                    f"하나의 질문만 반환해주시기 바랍니다."
                )
                question_response = chat.invoke([SystemMessage(content=prompt)])
                korean_job_question = question_response.content.strip()

                model_prompt = model_answer(korean_job_question, retrieved_content)
                model_response = chat.invoke([SystemMessage(content=model_prompt)])
                korean_job_solution = model_response.content.strip()

                add_question(korean_job_question, korean_job_solution, retrieved_content, combined_keywords)

    return questions
