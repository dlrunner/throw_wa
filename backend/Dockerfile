# 베이스 이미지 python 3.12 사용
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# portaudio 및 ffmpeg 라이브러리 설치
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg

# requirements.txt 파일을 컨테이너로 복사하기 위함
COPY requirements.txt /app/

# 종속성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 어플리케이션 파일을 컨테이너로 복사
COPY . /app

# FASTAPI 실행될 포트 설정
EXPOSE 8000

# 컨테이너 실행시 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]