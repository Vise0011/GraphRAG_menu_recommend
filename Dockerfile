# 1. 베이스 이미지 (Python 3.11)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 시스템 의존성 설치 (Git 등 필요할 수 있음)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 노출
EXPOSE 8000

# 7. 실행 명령어 (서버 시작)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
