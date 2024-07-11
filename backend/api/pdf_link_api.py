import urllib.parse
import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import PyPDF2
import platform
from database.database import Database
from database.vector_db import VectorDatabase
from models.embedding import embed_text  # Import the embedding function
import numpy as np
import httpx

router = APIRouter()

# MySQL 데이터베이스 연결 설정
db_config = {
    'host': '127.0.0.1',
    'user': 'nlrunner',
    'password': 'nlrunner',
    'database': 'nlrunner_db'
}
db = Database(**db_config)
db.connect()
db.create_table()

class PDFUrl(BaseModel):
    url: str  # pdf_path에서 url로 변경

def extract_text_from_local_pdf(pdf_url: str) -> str:
    # URL 디코딩
    decoded_path = urllib.parse.unquote(pdf_url)
    
    # 파일 프로토콜 제거
    if platform.system() == "Windows":
        if decoded_path.startswith("file:///"):
            decoded_path = decoded_path[8:]
    elif platform.system() == "Darwin":  # macOS
        if decoded_path.startswith("file://"):
            decoded_path = decoded_path[7:]

    
    # 경로 구분자 변경
    decoded_path = decoded_path.replace("/", os.path.sep)
    
    if not os.path.exists(decoded_path):
        raise FileNotFoundError(f"File not found: {decoded_path}")
    
    with open(decoded_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    return text

# 엔드포인트
@router.post("/pdf_text")
async def extract_local_pdf(pdf_url: PDFUrl):
    try:
        extracted_text = extract_text_from_local_pdf(pdf_url.url)
        id = db.insert_pdf(pdf_url.url, extracted_text)
        embedding = embed_text(extracted_text)

        payload = {
        "id": str(id),
        "embedding" : embedding,
        "link" : pdf_url.url
    }

        spring_url = "http://localhost:8080/api/embedding"
        async with httpx.AsyncClient() as client:
            try:
                spring_response = await client.post(spring_url, json=payload)
                spring_response.raise_for_status()
                print(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to Spring Boot server: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결할 수 없습니다.")
            

        return {"success": True, "text": extracted_text, "embedding": embedding}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# call_pdf 함수 정의
async def call_pdf(link: str):
    request = PDFUrl(url=link)
    return await extract_local_pdf(request)
