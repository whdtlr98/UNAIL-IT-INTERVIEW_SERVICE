import boto3
import io
import fitz  # PyMuPDF
import logging
import pandas as pd
import re
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from util.get_parameter import get_parameter




# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")




def extract_s3_key(s3_path: str) -> str:

    # 정규표현식으로 "s3://버킷 이름/" 제거
    match = re.match(r"s3://[^/]+/(.+)", s3_path)
    if match:
        return match.group(1)  # Key 부분 반환
    raise ValueError(f"Invalid S3 path: {s3_path}")

class ResumePathManager:
    resume_path = None

    @classmethod
    def set_path(cls, path):
        cls.resume_path = path

    @classmethod
    def get_path(cls):
        if not cls.resume_path:
            raise ValueError("RESUME_PATH is not set.")
        return cls.resume_path

# S3에서 파일 로드 함수
def load_pdf_from_s3(bucket_name, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_stream = response['Body']

    # 경로저장
    s3_path = f"s3://{bucket_name}/{key}"
    formatted_key = extract_s3_key(s3_path)
    ResumePathManager.set_path(formatted_key)

    return io.BytesIO(file_stream.read())


# PDF 내용을 메모리에서 읽는 함수 (PyMuPDF 사용)
# PyPDFLoader는 파일 경로 또는 URL만을 지원하므로 io.BytesIO 객체를 바로 입력할 수 없음
# 이를 해결하려면 메모리의 파일 데이터를 처리할 수 있도록 PyPDFLoader 대신 PyMuPDF 또는 pdfplumber 같은 다른 라이브러리를 사용
def load_pdf_content_from_stream(file_stream):
    pdf_content = ""
    with fitz.open(stream=file_stream, filetype="pdf") as doc:
        for page in doc:
            pdf_content += page.get_text()
    return pdf_content

# 텍스트 전처리 함수
def preprocess_text(text):
    lines = text.split('\n')
    processed_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(processed_lines)

# Pydantic 모델 정의
class ResumeProject(BaseModel):
    project: str = Field(description="프로젝트 경험")

# 프로젝트 경험 추출 함수
def extract_project_experience(text, api_key):
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o")
    parser = PydanticOutputParser(pydantic_object=ResumeProject)
    prompt = PromptTemplate.from_template(
        """
        You are a helpful assistant.

        QUESTION:
        {question}

        RESUME:
        {resume}

        FORMAT:
        {format}
        """
    )
    prompt = prompt.partial(format=parser.get_format_instructions())
    template_chain = prompt | llm | parser
    response = template_chain.invoke({
        "resume": text,
        "question": "이력서 내용 중 프로젝트 경험을 추출해주세요."
    })

    return response.project

# 번역 함수
def translate_text(text, api_key):
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini")
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional translator. Please translate Korean to English"),
        ("user", "{input_text}")
    ])
    chain = chat_prompt | llm
    result = chain.invoke({"input_text": text})
    return result.content

# 키워드 추출 함수
def extract_keywords(text_chunks):
    tokenizer = AutoTokenizer.from_pretrained("ilsilfverskiold/tech-keywords-extractor")
    model = AutoModelForSeq2SeqLM.from_pretrained("ilsilfverskiold/tech-keywords-extractor")

    
    keywords = ""
    for value in text_chunks:
        inputs = tokenizer.encode("extract tech keywords: " + value, return_tensors="pt", max_length=500, truncation=True)
        outputs = model.generate(inputs, max_length=30, num_beams=4, num_return_sequences=3, repetition_penalty=1, early_stopping=True)
        keywords += tokenizer.decode(outputs[0], skip_special_tokens=True)
    return keywords


# 정규표현식 함수(키워드 문자열을 쉼표와 공백으로 구분된 형태로 변환)
def format_keywords(keywords: str) -> str:
    # 단어 경계를 기준으로 쉼표 추가
    cleaned_keywords = re.sub(r'(?<=[a-zA-Z0-9])(?=[A-Z])', ', ', keywords)  # PascalCase 구분
    cleaned_keywords = re.sub(r'\s+', ' ', cleaned_keywords)  # 연속된 공백 처리
    cleaned_keywords = re.sub(r',+', ',', cleaned_keywords)  # 중복된 쉼표 처리
    return ", ".join([kw.strip() for kw in cleaned_keywords.split(",") if kw.strip()])



# 메인 함수
def keyword_main(user_id):
    
    try:
        logging.info("프로그램 시작")

        # API 키 및 S3 설정
        OPENAI_API_KEY = get_parameter('/TEST/CICD/STREAMLIT/OPENAI_API_KEY')
        S3_BUCKET = "sk-unailit"
        file_name = f"resume_{user_id}.pdf"  # 파일명 동적 생성

        # 입력 경로
        INPUT_KEY = f"resume/{user_id}/{file_name}"
        print("INPUT_KEY : ", INPUT_KEY)

        # S3에서 PDF 불러오기
        file_stream = load_pdf_from_s3(S3_BUCKET, INPUT_KEY)
        pdf_text = preprocess_text(load_pdf_content_from_stream(file_stream))

        # 프로젝트 경험 추출
        project_experience = extract_project_experience(pdf_text, OPENAI_API_KEY)
        logging.info("[Extracted Project Experience]:\n" + project_experience)

        # 번역
        translated_text = translate_text(project_experience, OPENAI_API_KEY)
        translated_text = translated_text.lower()
        logging.info("[Translated Project Experience]:\n" + translated_text)


        # 텍스트 청크화 및 키워드 추출
        chunk_size = 500
        text_chunks = [translated_text[i:i + chunk_size] for i in range(0, len(translated_text), chunk_size)]
        keywords = extract_keywords(text_chunks)
        logging.info("[Extracted Keywords]:\n" + keywords)
        
        formatted_keywords = format_keywords(keywords)  # 포맷팅 적용
        logging.info(f"Formatted Keywords: {formatted_keywords}")
        return formatted_keywords

    except Exception as e:
        logging.error("에러 발생: ", exc_info=True)

# if __name__ == "__main__":
#     main()