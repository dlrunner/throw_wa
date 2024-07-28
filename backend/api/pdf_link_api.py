import os
import shutil
import PyPDF2
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from pydantic import BaseModel
from database.database_config import DatabaseConfig
from models.embedding import embed_text
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title
from dotenv import load_dotenv
import logging

router = APIRouter()

# MySQL 데이터베이스 설정
db_config = DatabaseConfig()
db = db_config.get_db()

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
spring_api_url = os.getenv("SPRING_API_URL")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# HTTP 클라이언트 세션 생성
client = httpx.AsyncClient(timeout=10.0)

class PDFUrl(BaseModel):
    url: str
    type: str = "PDF"
    date: str
    userId: str
    userName: str

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # 임시 파일 경로 설정
        temp_file_path = f"/tmp/{file.filename}"

        # 파일 저장
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        # PDF 텍스트 추출
        extracted_text = await extract_text_from_local_pdf(temp_file_path)

        # 로컬 파일 경로 생성
        local_file_path = f"file://{os.path.abspath(temp_file_path)}"

        # 데이터베이스에 저장
        id = db.insert_pdf(file.filename, extracted_text)
        embedding = embed_text(extracted_text)
        summary_text = await generate_summary(extracted_text)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)

        # PDF 파일을 S3로 업로드
        try:
            s3_info = await upload_pdf_to_s3(temp_file_path, file.filename)
        except Exception as e:
            logger.error(f"PDF 업로드 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"PDF 업로드 중 오류 발생: {e}")

        # Spring Boot 서버로 데이터 전송
        payload = {
            "id": str(id),
            "embedding": embedding,
            "link": local_file_path,
            "type": "PDF",
            "date": "",
            "summary": str(summary_text),
            "keyword": str(keyword),
            "title": str(show_title),
            "s3OriginalFilename": str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url']),
            "userId": "",
            "userName": ""
        }

        spring_url = f"{spring_api_url}/api/embeddingS3"
        try:
            logger.info(f"Sending data to Spring Boot: {spring_url}")
            spring_response = await client.post(spring_url, json=payload)
            spring_response.raise_for_status()
            logger.info(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
        except AttributeError as e:
            logger.error(f"Spring Boot 서버 연결 중 응답 오류: {e}")
            raise HTTPException(status_code=500, detail=f"Spring Boot 서버 연결 중 응답 오류: {str(e)}")

        return {
            "success": True,
            "text": extracted_text,
            "summary": summary_text,
            "title": show_title,
            "keyword": keyword,
            "embedding": embedding,
            "s3OriginalFilename": str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url']),
            "userId": "",
            "userName": ""
        }
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"임시 PDF 파일 삭제: {temp_file_path}")

async def extract_text_from_local_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"파일에서 텍스트 추출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"파일에서 텍스트 추출 중 오류 발생: {str(e)}")

async def upload_pdf_to_s3(file_path: str, file_name: str):
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()

        files = {'file': (file_name, file_content)}
        logger.info(f"Uploading PDF to Spring Boot: {spring_api_url}/api/upload")
        response = await client.post(f"{spring_api_url}/api/upload", files=files)
        response.raise_for_status()

        # Spring Boot에서 반환한 JSON 응답을 파싱
        result = response.json()
        return result
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"오류: {str(e)}")

app.include_router(router)
