from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from .make_loader import csvloader_data, html_loader_data
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
# embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# 텍스트 분할기 및 임베딩 초기화
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)

# 1. 문서 로드 (csvloader_data/html_loader_data)
docs = csvloader_data()  # 이미 Document 객체로 로드된 상태

# 2. Document 객체 리스트 분할
split_doc1 = text_splitter.split_documents(docs)  # Document 리스트를 분할

print(split_doc1)
# 3. DB 생성
db = FAISS.from_documents(documents=split_doc1, embedding=embedding_model)

index_name = "python_new_low_chunk700"

# 4. 새로운 Document 객체 추가 함수
def add_documents(db, new_docs):

    # 새로운 문서의 임베딩을 생성하고 DB에 추가
    db.add_documents(new_docs)
    db.save_local(folder_path="low_db", index_name=index_name)

# 사용 예시
new_docs = csvloader_data()  
new_split_docs = text_splitter.split_documents(new_docs)  # Document 객체 리스트 분할

add_documents(db, new_docs)

