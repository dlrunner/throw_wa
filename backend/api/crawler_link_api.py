import requests
from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
import torch
import mysql.connector
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import pickle
from database import Database

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

# 크롤링 함수 (각 사이트마다 html 태그가 다름 따라서 사이트 별 태그 분석 후 모듈화 필요)
def crawl_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        content = " ".join([p.text for p in soup.find_all('p')])
        return title, content
    else:
        return None, None


# 임베딩 함수
def embed_text(text: str) -> list :
    tokenizer = AutoTokenizer.from_pretrained('klue/bert-base') # 모델은 transformers의 klue/bert-base 영어 한국어 지원 모델
    model = AutoModel.from_pretrained('klue/bert-base')         # pip install transformers torch 설치 필요

    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    embeddings = torch.mean(outputs.last_hidden_state, dim=1)
    return embeddings.detach().numpy().tolist()


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
        "content" : content,
        "embedding" : embedding
    }

# call_crawler 함수 정의
async def call_crawler(link : str) :
    request = Bookmark(url=link)
    return await add_bookmark(request)

