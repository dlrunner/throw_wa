from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, APIRouter
from database.vector_db import VectorDatabase
import numpy as np

router = APIRouter()

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

class VectorUpsertRequest(BaseModel):
    id: str
    embedding: list[float]
    link: str

@router.post("/vector_upsert")
async def vector_upsert(request: VectorUpsertRequest):
    try:

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=request.id,
            vector=request.embedding,
            metadata={"link": request.link}
        )

        return {"success": True}
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
