import urllib.parse
import os
import urllib.parse
import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import PyPDF2
from database.database import Database
from transformers import BertTokenizer, BertModel , AutoTokenizer, AutoModel
import torch
from database.vector_db import VectorDatabase

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

# 백터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="vector",
    dimension=768
)

class PDFUrl(BaseModel):
    url: str  # pdf_path에서 url로 변경

def extract_text_from_local_pdf(pdf_url: str) -> str:
    # URL 디코딩
    decoded_path = urllib.parse.unquote(pdf_url)
    
    # 파일 프로토콜 제거
    if decoded_path.startswith("file:///"):
        decoded_path = decoded_path[8:]
    
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

# 로컬 pdf파일 링크로 텍스트 추출
def extract_text_from_local_pdf(pdf_url: str) -> str:
    # URL 디코딩
    decoded_path = urllib.parse.unquote(pdf_url)
    
    # 파일 프로토콜 제거 이유: file:/// 은 못읽음. 제거 필요
    if decoded_path.startswith("file:///"):
        decoded_path = decoded_path[8:]
    
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

# 임베딩 함수
def embed_text(text: str) -> list :
    tokenizer = AutoTokenizer.from_pretrained('klue/bert-base') # 모델은 transformers의 klue/bert-base 한국어 임베딩 지원 모델
    model = AutoModel.from_pretrained('klue/bert-base')         # pip install transformers torch 설치 필요

    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    # BERT 모델의 출력에서 평균을 구하여 리스트 형태로 변환
    embeddings = torch.mean(outputs.last_hidden_state, dim=1).squeeze().detach().numpy().tolist()
    return embeddings


# 엔드포인트
@router.post("/pdf_text")
async def extract_local_pdf(pdf_url: PDFUrl):
    try:
        extracted_text = extract_text_from_local_pdf(pdf_url.url)
        pdf_id = db.insert_pdf(pdf_url.url,extracted_text)
        embedding = embed_text(extracted_text)

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=str(pdf_id),
            vector=embedding,
            metadata={"source": extracted_text}
        )
        return {"success": True, "text": extracted_text, "embedding": embedding}  # success 필드 추가 text embedding 
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# call_pdf 함수 정의
async def call_pdf(link:str):
    request = PDFUrl(url=link)
    return await extract_local_pdf(request)