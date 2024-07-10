import requests
from bs4 import BeautifulSoup
from transformers import CLIPProcessor, CLIPModel , AutoTokenizer, AutoModel
import torch
import mysql.connector
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import pickle
from database.database import Database
from database.vector_db import VectorDatabase
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

# 텍스트 임베딩 모델
model_name = "intfloat/multilingual-e5-small"
processor = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    # 텍스트를 최대 길이 77로 분할
    max_length = 77
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    embeddings = []
    for chunk in text_chunks:
        inputs = processor(chunk, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
            text_features = outputs.last_hidden_state.mean(dim=1)  # BERT 모델의 임베딩 추출 방식
        embeddings.append(text_features.squeeze().cpu().numpy())
    
    # 모든 청크 임베딩의 평균을 계산
    mean_embedding = np.mean(embeddings, axis=0)
    return mean_embedding.tolist()


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

    id = db.insert_crawling(url, title, content)
    embedding = embed_text(content)

    payload = {
        "id": str(id),
        "embedding" : embedding,
        "link" : url
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

 
    return {
        "success": True,
        "id": id,
        "url": url,
        "title": title,
        "content_length": len(content),
        "content": content,
        "embedding": embedding
    }


