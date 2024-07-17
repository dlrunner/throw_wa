# api/crawler_link_api.py
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import embed_text  # 임베딩 함수 호출
from database.database import Database
from database.vector_db import VectorDatabase
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title  # 제목 추출
import httpx

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
    type: str = "web"
    date: str

# Add bookmark endpoint
@router.post("/crawler")
async def add_bookmark(bookmark: Bookmark):
    url = bookmark.url
    title, content = crawl_data(url)
    if not title or not content:
        raise HTTPException(status_code=500, detail="이 웹사이트는 크롤링을 할 수 없습니다.")

    # 크롤링한 데이터를 DB에 저장
    try:
        id = db.insert_crawling(url, title, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")

    # 콘텐츠 임베딩 생성
    embedding = embed_text(content)

    # 콘텐츠 요약 및 키워드 생성
    try:
        summary_text = await generate_summary(content)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 처리 오류: {str(e)}")

    payload = {
        "id": str(id),
        "embedding": embedding,
        "link": url,
        "type": bookmark.type,
        "date": bookmark.date,
        "summary": str(summary_text),
        "keyword": str(keyword),
        "title": str(show_title)
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
        "embedding": embedding,
        "date": bookmark.date
    }
