import pandas as pd
from sentence_transformers import SentenceTransformer
from .keyword_s3 import get_parameter, load_pdf_from_s3, load_pdf_content_from_stream, preprocess_text
from sklearn.metrics.pairwise import cosine_similarity
import os

file_path = os.path.abspath("SKN03-FINAL-5Team/backend/data/cs_interview.xlsx")
print(file_path)
df = pd.read_excel(r"C:\Users\woncheol\Desktop\final project\SKN03-FINAL-5Team\backend\data\cs_interview.xlsx")

# df = pd.read_excel("../data/cs_interview.xlsx")

def question_similarity_main(i, USER_ID):
    # API 키 및 S3 설정
    OPENAI_API_KEY = get_parameter('/interviewdb-info/OPENAI_API_KEY')
    S3_BUCKET = "sk-unailit"
    id = USER_ID
    file_name = f"resume_{id}.pdf"  # 파일명 동적 생성
    
    # 입력 경로
    INPUT_KEY = f"resume/{id}/{file_name}"
    print("INPUT_KEY:", INPUT_KEY)

    # S3에서 PDF 불러오기
    file_stream = load_pdf_from_s3(S3_BUCKET, INPUT_KEY)
    pdf_text = preprocess_text(load_pdf_content_from_stream(file_stream))
    print("Extracted PDF Text:", pdf_text)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 이력서 텍스트 임베딩
    resume_embedding = model.encode(pdf_text)

    # 답변 텍스트 임베딩
    questions = df["question"].tolist()  # 질문 리스트
    answers = df["answer"].tolist()      # 답변 리스트
    answer_embeddings = model.encode(answers)

    # 유사도 계산
    similarities = cosine_similarity([resume_embedding], answer_embeddings)[0]

    # 상위 5개의 유사도 및 인덱스
    top_5_indices = similarities.argsort()[-5:][::-1]  # 상위 5개의 인덱스 (내림차순)
    top_5_similarities = similarities[top_5_indices]  # 상위 5개의 유사도
    top_5_questions = [questions[i] for i in top_5_indices]  # 상위 5개의 질문
    top_5_answers = [answers[i] for i in top_5_indices]  # 상위 5개의 답변

    # # 출력
    # print("\n가장 유사한 질문 및 답변과 유사도:")
    # for rank, (question, answer, similarity_score) in enumerate(zip(top_5_questions, top_5_answers, top_5_similarities), start=1):
    #     print(f"{rank}. 질문: {question}")
    #     print(f"   답변: {answer}")
    #     print(f"   유사도: {similarity_score:.4f}\n")

    return top_5_questions, top_5_answers

# , top_5_similarities
# if __name__ == "__question_similarity_main__":
#     question_similarity_main()
