from fastapi import APIRouter, HTTPException
from database.vector_db import VectorDatabase

router = APIRouter()

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
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
        
        return {"rankings": [{"keyword": keyword, "count": count} for keyword, count in keyword_rankings]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 랭킹 호출 실패: {str(e)}")
