FROM python:3.10.12-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

ENV SERVER_ENV=k8s

# Gunicorn을 통한 실행
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application"]
