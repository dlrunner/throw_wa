# api/image_link_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import imagecaption, embed_text  # 임베딩 함수 호출
from database.database import Database
from database.vector_db import VectorDatabase

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

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

class ImageEmbRequest(BaseModel):
    url: str

@router.post("/image_embedding")
async def get_image_embedding_endpoint(request: ImageEmbRequest):
    try:
        # 이미지 캡셔닝 및 텍스트 임베딩 함수 호출
        caption, _ = imagecaption(request.url)
        
        # E5 모델을 사용하여 텍스트 임베딩
        text_embedding = embed_text(caption)

        # 데이터베이스에 결과 저장 (원본 영어 캡션만 저장)
        image_id = db.insert_image(request.url, caption)

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=str(image_id),
            vector=text_embedding,
            metadata={"link": request.url}
        )

        # 결과 준비
        results = {
            "success": True,
            "image_url": request.url,
            "이미지 캡셔닝 결과": caption,
            "텍스트 임베딩값": text_embedding
        }

        print("모든 처리 완료")
        return results
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
