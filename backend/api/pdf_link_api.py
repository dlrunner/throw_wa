import urllib.parse
import os
import urllib.parse
import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import PyPDF2
from database.database import Database
from transformers import CLIPProcessor, CLIPModel
import torch
from database.vector_db import VectorDatabase
import numpy as np

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

# CLIP 모델 및 프로세서 로드
model_name = "openai/clip-vit-large-patch14"
processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)

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


# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    # 텍스트를 최대 길이 77로 분할
    max_length = 77
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    embeddings = []
    for chunk in text_chunks:
        inputs = processor(text=[chunk], return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        embeddings.append(text_features.squeeze().cpu().numpy())
    
    # 모든 청크 임베딩의 평균을 계산
    mean_embedding = np.mean(embeddings, axis=0)
    return mean_embedding.tolist()


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
            metadata={"link": pdf_url.url}
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