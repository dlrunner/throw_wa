# main.py
from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import List
from pydantic import BaseModel
from database.vector_db import VectorDatabase
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter()

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

class Bookmark(BaseModel):
    url: str
    date: str

@router.get("/record", response_model=List[Bookmark])
async def get_record(date: str = Query(..., description="The date to filter bookmarks by")):
    try:
        # 메타데이터를 기반으로 검색
        metadata_filter = {"date": date}
        response = vector_db.search_by_metadata(metadata_filter)
        data = response["matches"]
        
        bookmarks = [
            Bookmark(url=item["metadata"]["link"], date=item["metadata"]["date"])
            for item in data
        ]
        return bookmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/recent-week", response_model=List[Bookmark])
async def recent_week():
    try:
        today = datetime.utcnow().date()
        last_week_dates = [(today - timedelta(days=i)).isoformat() for i in range(7)]

        bookmarks = []
        for date in last_week_dates:
            metadata_filter = {"date": date}
            response = vector_db.search_by_metadata(metadata_filter)
            data = response["matches"]
            for item in data:
                bookmarks.append(Bookmark(url=item["metadata"]["link"], date=item["metadata"]["date"]))
                
        return bookmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
