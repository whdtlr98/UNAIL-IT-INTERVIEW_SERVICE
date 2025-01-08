import pdfplumber

pdf_path = 'c:/dev/SKN03-Final_Project/이력서_20240508.pdf'
def resume_loader(pdf_path):
    resume_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            resume_text += page.extract_text() + "\n"  # 각 페이지의 텍스트를 추가
    return resume_text

text = resume_loader(pdf_path)
print(text)

# resume_loader 함수가 파일 객체를 받도록 수정
def resume_loader(file_obj):
    with pdfplumber.open(file_obj) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# 외부에서 파일을 업로드받아 텍스트로 변환 후 상태에 전달
uploaded_file = request.files['resume']  # 가정: 업로드된 파일
resume_text = resume_loader(uploaded_file)