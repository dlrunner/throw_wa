import urllib.parse
import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import httpx
from database.database_config import DatabaseConfig
from database.vector_db import VectorDatabase
from models.embedding import embed_text  # Import the embedding function
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title # 제목 추출
import PyPDF2
import aiofiles  # 파일 추출
from dotenv import load_dotenv

app = FastAPI()
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

async def download_pdf(pdf_url: str):
    try:
        # 파일 이름 추출 및 처리
        real_pdf_url = pdf_url.replace('%20', ' ')
        file_name = real_pdf_url.split('/')[-1]

        if real_pdf_url.startswith("file:///") or os.path.exists(real_pdf_url):
            # 로컬 파일 경로인 경우
            local_path = real_pdf_url.replace('file:///', '')
            async with aiofiles.open(local_path, 'rb') as file:
                file_content = await file.read()
        else:
            # 웹 URL인 경우
            async with httpx.AsyncClient() as client:
                response = await client.get(real_pdf_url)
                response.raise_for_status()
                file_content = response.content

        # 파일 내용을 Spring Boot로 전송
        files = {'file': (file_name, file_content)}
        async with httpx.AsyncClient() as client:
            response = await client.post(spring_api_url + "/api/upload", files=files)
            response.raise_for_status()

        # Spring Boot에서 반환한 JSON 응답을 파싱
        result = response.json()
        return result
    except httpx.HTTPError as e:
        print(f"HTTP 오류 발생: {e.status_code}")
        raise HTTPException(status_code=500, detail=f"HTTP 오류 발생: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"오류 발생: {e}")

async def extract_text_from_url(pdf_url: str) -> str:
    try:
        if pdf_url.startswith("file:///") or os.path.exists(pdf_url):
            # 로컬 파일 경로인 경우
            decoded_path = urllib.parse.unquote(pdf_url.replace('file:///', ''))
            async with aiofiles.open(decoded_path, 'rb') as file:
                file_content = await file.read()
        else:
            # 웹 URL인 경우
            async with httpx.AsyncClient() as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                file_content = response.content

        # PDF 내용 추출
        with open("/tmp/temp.pdf", "wb") as f:
            f.write(file_content)
        
        with open("/tmp/temp.pdf", "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        return text
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"파일 다운로드 중 오류 발생: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")

@router.post("/pdf_text")
async def extract_pdf(pdf_url: PDFUrl):
    try:
        extracted_text = await extract_text_from_url(pdf_url.url)
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
            "embedding": embedding,
            "link": pdf_url.url,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

