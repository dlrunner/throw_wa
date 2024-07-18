from fastapi import APIRouter, HTTPException
from database.vector_db import VectorDatabase
import os

router = APIRouter()

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key= os.getenv("PINECONE_API_KEY"),
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

@router.get("/keyword-rankings")
async def get_keyword_rankings():
    try:
        keyword_rankings = vector_db.get_keword_rankings()
        if not keyword_rankings:
            return {"rankings": []}
        
        return {"rankings": keyword_rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 랭킹 호출 실패: {str(e)}")
