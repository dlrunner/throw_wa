import requests
from bs4 import BeautifulSoup
from transformers import CLIPProcessor, CLIPModel
import torch
import mysql.connector
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import pickle
from database.database import Database
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

# 크롤링 함수
def crawl_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        content = " ".join([p.text for p in soup.find_all('p')])
        return title, content
    else:
        return None, None

# CLIP 모델 및 프로세서 로드
model_name = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)

# 임베딩 함수
def embed_text(text: str) -> list :
    tokenizer = AutoTokenizer.from_pretrained('klue/bert-base') # 모델은 transformers의 klue/bert-base 영어 한국어 지원 모델
    model = AutoModel.from_pretrained('klue/bert-base')         # pip install transformers torch 설치 필요

    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    # BERT 모델의 출력에서 평균을 구하여 리스트 형태로 변환
    embeddings = torch.mean(outputs.last_hidden_state, dim=1).squeeze().detach().numpy().tolist()
    return embeddings


# Bookmark model
class Bookmark(BaseModel):
    url: str

# Add bookmark endpoint
@router.post("/crawler")
async def add_bookmark(bookmark: Bookmark):
    url = bookmark.url
    title, content = crawl_data(url)
    if not title or not content:
        raise HTTPException(status_code=500, detail="이 웹사이트는 크롤링을 할 수 없습니다.")

    crawling_id = db.insert_crawling(url, title, content)
    embedding = embed_text(content)

    # 벡터 디비에 upsert
    vector_db.upsert_vector(
        vector_id=str(crawling_id),
        vector=embedding,
        metadata={"source": url}
    )

    return {
        "success": True,
        "id": crawling_id,
        "url": url,
        "title": title,
        "content_length": len(content),
        "content": content,
        "embedding": embedding
    }

# call_crawler 함수 정의
async def call_crawler(link : str) :
    request = Bookmark(url=link)
    return await add_bookmark(request)

