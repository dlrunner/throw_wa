
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import imagecaption, embed_text, translate_text  # 번역 함수 수정
from database.database import Database
from database.vector_db import VectorDatabase
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

class ImageEmbRequest(BaseModel):
    url: str
    type: str = "image"
    date: str

@router.post("/image_embedding")
async def get_image_embedding_endpoint(request: ImageEmbRequest):
    try:
        # 이미지 캡셔닝 및 텍스트 생성
        caption = imagecaption(request.url)
        
        # 번역 텍스트 생성
        transcaption = translate_text(caption)
        
        # E5 모델을 사용하여 번역된 한글 텍스트 임베딩
        embedding = embed_text(transcaption)

        # 데이터베이스에 결과 저장 (번역된 한국어 캡셔닝만 저장)
        image_id = db.insert_image(request.url, transcaption)

        # 결과 준비
        results = {
            "success": True,
            "image_url": request.url,
            "original_caption": caption,
            "translated_caption": transcaption,
            "텍스트 임베딩값": embedding
        }

        payload = {
            "id": str(image_id),
            "embedding": embedding,
            "link": request.url,
            "type": request.type,
            "date": request.date
        }

        spring_url = "http://localhost:8080/api/embedding"
        async with httpx.AsyncClient() as client:
            try:
                spring_response = await client.post(spring_url, json=payload)
                spring_response.raise_for_status()
                print(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결 중 HTTP 오류가 발생했습니다.")
            except httpx.RequestError as e:
                print(f"Request error: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결 중 요청 오류가 발생했습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    print("모든 처리 완료")
    return results
