import requests
from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertModel
import torch
import mysql.connector
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import pickle
from database import Database

# Define the FastAPI app
router = APIRouter()

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

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

# Crawl data function
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
    
    # Step 1: Web Crawling
    title, content = crawl_data(url)
    if not title or not content:
        raise HTTPException(status_code=500, detail="Unable to crawl the webpage.")
    print(f"Web crawling completed: title='{title[:30]}', content length={len(content)}")

    crawling_id = db.insert_crawling(url, title, content)

    return {
        "success": True,
        "id": crawling_id,
        "url": url,
        "title": title,
        "content_length": len(content)
    }

