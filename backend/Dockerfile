# 베이스 이미지 python 3.12 사용
FROM nvcr.io/nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# 환경 변수 설정 (비대화형 모드)
ENV DEBIAN_FRONTEND=noninteractive

# 작업 디렉토리 설정
WORKDIR /app

# portaudio 라이브러리 설치
RUN apt-get update && apt-get install -y portaudio19-dev git

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev && \
    rm -rf /var/lib/apt/lists/*

# Python 3.12 다운로드 및 설치
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar xzf Python-3.12.0.tgz && \
    cd Python-3.12.0 && \
    ./configure -enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.0 Python-3.12.0.tgz

# pip 설치 및 업그레이드
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# pip와 python 명령어 심볼릭 링크 설정
# RUN ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip && \
#     ln -s /usr/local/bin/python3.12 /usr/local/bin/python

# Python3.12와 pip가 설치되었는지 확인
RUN python3.12 --version && pip3.12 --version

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
