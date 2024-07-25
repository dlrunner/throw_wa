import urllib.parse
import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import PyPDF2
import platform
from database.database_config import DatabaseConfig
from database.vector_db import VectorDatabase
from models.embedding import embed_text  # Import the embedding function
import numpy as np
import httpx
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title # 제목 추출
import aiofiles # 파일 추출
from dotenv import load_dotenv

router = APIRouter()

# MySQL 데이터베이스 설정
db_config = DatabaseConfig()
db = db_config.get_db()

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
spring_api_url = os.getenv("SPRING_API_URL")

class PDFUrl(BaseModel):
    url: str  # pdf_path에서 url로 변경
    type: str = "PDF"
    date: str

async def download_pdf(file_path: str):
    try:
        file_name = os.path.basename(file_path)

        async with aiofiles.open(file_path, 'rb') as file:
            file_content = await file.read()

        files = {'file': (file_name, file_content)}
        async with httpx.AsyncClient() as client:
            response = await client.post(spring_api_url + "/api/upload", files=files)
            response.raise_for_status()

        result = response.json()
        return result
    except httpx.HTTPError as e:
        print(f"HTTP 오류 발생: {e.status_code}")
    except Exception as e:
        print(f"오류 발생: {e}")

async def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류 발생: {str(e)}")

@router.post("/pdf_text")
async def extract_pdf(pdf_url: PDFUrl):
    # 경로 디코딩 및 검증
    decoded_path = urllib.parse.unquote(pdf_url.url)

    # 파일 존재 여부 확인
    if not os.path.exists(decoded_path):
        raise HTTPException(status_code=404, detail=f"File not found: {decoded_path}")

    extracted_text = await extract_text_from_pdf(decoded_path)
    id = db.insert_pdf(decoded_path, extracted_text)
    embedding = embed_text(extracted_text)
    summary_text = await generate_summary(extracted_text)
    keyword = await keyword_extraction(summary_text)
    show_title = await generate_title(summary_text)

    try:
        s3_info = await download_pdf(decoded_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 다운로드 중 오류 발생: {str(e)}")

    payload = {
        "id": str(id),
        "embedding": embedding,
        "link": decoded_path,
        "type": pdf_url.type,
        "date": pdf_url.date,
        "summary": str(summary_text),
        "keyword": str(keyword),
        "title": str(show_title),
        "s3OriginalFilename": str(s3_info['originalFilename']),
        "s3Key": str(s3_info['key']),
        "s3Url": str(s3_info['url'])
    }

    spring_url = spring_api_url + "/api/embeddingS3"
    async with httpx.AsyncClient() as client:
        try:
            spring_response = await client.post(spring_url, json=payload)
            spring_response.raise_for_status()
            print(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
        except httpx.HTTPError as e:
            print(f"Error connecting to Spring Boot server: {str(e)}")
            raise HTTPException(status_code=500, detail="스프링 서버와 연결할 수 없습니다.")

    return {
        "success": True,
        "text": extracted_text,
        "summary": summary_text,
        "title": show_title,
        "keyword": keyword,
        "embedding": embedding,
        "s3OriginalFilename": str(s3_info['originalFilename']),
        "s3Key": str(s3_info['key']),
        "s3Url": str(s3_info['url'])
    }

