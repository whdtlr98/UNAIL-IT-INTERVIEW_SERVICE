# Python 베이스 이미지
FROM python:3.9-slim

# OS 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# 작업 디렉터리 설정
WORKDIR /app

# FastAPI 코드와 요구사항 복사
COPY . /app
COPY requirements.txt /app

# Python 종속성 설치
RUN pip install -r requirements.txt

# 애플리케이션 실행 포트 설정

EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]