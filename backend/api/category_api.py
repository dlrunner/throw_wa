from fastapi import APIRouter, HTTPException
from typing import Dict, List
from database.vector_db import VectorDatabase

router = APIRouter()

# Pinecone 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

@router.get("/category-data")
async def get_category_data() -> Dict[str, List[Dict[str, str]]]:
    try:
        categorized_data = vector_db.get_top_n_by_type(5)
        if not categorized_data:
            return {"message": "No data found"}
        return categorized_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터를 가져오는 중 오류 발생: {str(e)}")
