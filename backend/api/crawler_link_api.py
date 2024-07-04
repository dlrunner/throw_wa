import requests
from bs4 import BeautifulSoup
from transformers import CLIPProcessor, CLIPModel
import torch
import mysql.connector
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import pickle
from database.database import Database

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
def embed_text(text: str) -> list:
    inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True, max_length=77)
    with torch.no_grad():
        outputs = model.get_text_features(**inputs)
    
    return outputs.squeeze().numpy().tolist()

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

