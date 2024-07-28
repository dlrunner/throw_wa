import os
import urllib.parse
import PyPDF2
import httpx
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from database.database_config import DatabaseConfig
from models.embedding import embed_text
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title
from dotenv import load_dotenv
import logging
import platform

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

# HTTP 클라이언트 세션 생성
client = httpx.AsyncClient(timeout=10.0)

class PDFUrl(BaseModel):
    url: str
    type: str = "PDF"
    date: str
    userId: str
    userName: str

async def download_pdf(pdf_url):
    try:
        real_pdf_url = pdf_url.replace('%20', ' ')
        file_name = real_pdf_url.split('/')[-1]

        logger.info(f"Downloading PDF from URL: {real_pdf_url}")
        # HTTP를 통해 PDF 파일 다운로드
        response = await client.get(real_pdf_url)
        response.raise_for_status()
        file_content = response.content

        # 파일 내용을 Spring Boot로 전송
        files = {'file': (file_name, file_content)}
        logger.info(f"Uploading PDF to Spring Boot: {spring_api_url}/api/upload")
        response = await client.post(f"{spring_api_url}/api/upload", files=files)
        response.raise_for_status()

        # Spring Boot에서 반환한 JSON 응답을 파싱
        result = response.json()
        return result
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 상태 오류 발생: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail=f"HTTP 상태 오류: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"HTTP 요청 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"HTTP 요청 오류: {str(e)}")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"오류: {str(e)}")

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
    finally:
        # 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"다운로드한 PDF 파일 삭제: {file_path}")

@router.post("/pdf_text")
async def extract_remote_pdf(pdf_url: PDFUrl):
    try:
        logger.info(f"Received request: {pdf_url}")
        
        file_name = pdf_url.url.split('/')[-1]
        file_path = f"/tmp/{file_name}"

        if pdf_url.url.startswith("file://"):
            # 로컬 파일 경로 처리
            decoded_path = urllib.parse.unquote(pdf_url.url)
            if platform.system() == "Windows":
                decoded_path = decoded_path[8:]  # 'file:///' 제거
            elif platform.system() == "Darwin":  # macOS
                decoded_path = decoded_path[7:]  # 'file://' 제거
            
            decoded_path = decoded_path.replace("/", os.path.sep)
            if not os.path.exists(decoded_path):
                raise HTTPException(status_code=404, detail="로컬 파일을 찾을 수 없습니다.")
            file_path = decoded_path
        else:
            # 원격 파일 다운로드
            async with client.stream("GET", pdf_url.url) as response:
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    async for chunk in response.aiter_bytes():
                        file.write(chunk)
        
        # 텍스트 추출
        extracted_text = await extract_text_from_local_pdf(file_path)
        
        # 데이터베이스에 저장
        id = db.insert_pdf(pdf_url.url, extracted_text)
        embedding = embed_text(extracted_text)
        summary_text = await generate_summary(extracted_text)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)

        # PDF 파일을 S3로 업로드
        try:
            s3_info = await download_pdf(pdf_url.url)
        except Exception as e:
            logger.error(f"PDF 다운로드 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"PDF 다운로드 중 오류 발생: {e}")

        # Spring Boot 서버로 데이터 전송
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
            "s3Url": str(s3_info['url']),
            "userId": pdf_url.userId,
            "userName": pdf_url.userName
        }

        spring_url = f"{spring_api_url}/api/embeddingS3"
        try:
            logger.info(f"Sending data to Spring Boot: {spring_url}")
            spring_response = await client.post(spring_url, json=payload)
            spring_response.raise_for_status()
            logger.info(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Spring Boot 서버 연결 오류: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, detail="스프링 서버와 연결할 수 없습니다.")
        except httpx.RequestError as e:
            logger.error(f"HTTP 요청 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"HTTP 요청 오류: {str(e)}")
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
            "userId": pdf_url.userId,
            "userName": pdf_url.userName
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 상태 오류 발생: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    except httpx.RequestError as e:
        logger.error(f"HTTP 요청 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"HTTP 요청 오류: {str(e)}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
