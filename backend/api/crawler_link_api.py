# api/crawler_link_api.py
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import embed_text  # 임베딩 함수 호출
from database.database import Database
from database.vector_db import VectorDatabase

router = APIRouter()

# MySQL 데이터베이스 설정
db_config = {
    'host': '127.0.0.1',
    'user': 'nlrunner',
    'password': 'nlrunner',
    'database': 'nlrunner_db'
}

try:
    db = Database(**db_config)
    db.connect()
    db.create_table()
except Exception as e:
    print(f"Database 연결 오류: {e}")
    raise

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
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

    try:
        crawling_id = db.insert_crawling(url, title, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database 삽입 오류: {e}")

    embedding = embed_text(content)  # 임베딩 함수 호출

    try:
        vector_db.upsert_vector(
            vector_id=str(crawling_id),
            vector=embedding,
            metadata={"link": url}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VectorDB 삽입 오류: {e}")

    return {
        "success": True,
        "id": crawling_id,
        "url": url,
        "title": title,
        "content_length": len(content),
        "content": content,
        "embedding": embedding
    }
