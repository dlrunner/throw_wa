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
    type : str = "PDF"
    date : str
    userId: str
    userName: str

async def download_pdf(pdf_url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            # 파일 이름 추출
            file_name = pdf_url.split('/')[-1]
            file_path = f"/tmp/{file_name}"  # 임시 파일 경로
            async with aiofiles.open(file_path, 'wb') as file:
                await file.write(response.content)
        return file_path
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"PDF 다운로드 중 오류 발생: {e}")

async def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        async with aiofiles.open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(await file.read())
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 텍스트 추출 중 오류 발생: {e}")

# 엔드포인트
@router.post("/pdf_text")
async def extract_pdf_text(pdf_url: PDFUrl):
    try:
        # PDF 다운로드
        downloaded_pdf_path = await download_pdf(pdf_url.url)
        
        # 텍스트 추출
        extracted_text = await extract_text_from_pdf(downloaded_pdf_path)
        
        # DB에 PDF 저장 및 임베딩
        id = db.insert_pdf(pdf_url.url, extracted_text)
        embedding = embed_text(extracted_text)
        summary_text = await generate_summary(extracted_text)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)

        try:
            s3_info = await download_pdf(pdf_url.url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF 다운로드 중 오류 발생: {str(e)}")

        payload = {
            "id": str(id),
            "embedding" : embedding,
            "link" : pdf_url.url,
            "type" : pdf_url.type,
            "date" : pdf_url.date,
            "summary": str(summary_text),
            "keyword" : str(keyword),
            "title" : str(show_title),
            "s3OriginalFilename" : str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url']),
            "userId": pdf_url.userId,
            "userName": pdf_url.userName
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
            "요약": summary_text,
            "title": show_title,
            "keyword" : keyword,
            "embedding": embedding,
            "s3OriginalFilename" : str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url']),
            "userId": pdf_url.userId,
            "userName": pdf_url.userName
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# call_pdf 함수 정의
async def call_pdf(link: str):
    request = PDFUrl(url=link)
    return await extract_pdf_text(request)
