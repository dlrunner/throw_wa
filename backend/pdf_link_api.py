import requests
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from PyPDF2 import PdfReader
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

class PDFRequest(BaseModel):
    url: str

@router.post("/pdf_text")
async def extract_text(request: PDFRequest):
    try:
        # PDF 다운로드
        response = requests.get(request.url)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        pdf_content = BytesIO(response.content)

        # PyPDF2를 사용하여 텍스트 추출
        reader = PdfReader(pdf_content)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() or ""  # None 타입일 경우 빈 문자열로 처리

        # 메타데이터 추출 (가능한 경우)
        metadata = reader.metadata
        title = metadata.get('/Title', 'Unknown')
        author = metadata.get('/Author', 'Unknown')

        return {
            "success": True,
            "title": title,
            "author": author,
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
