from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import imagecaption, embed_text, translate_text  # 번역 함수 수정
from database.database_config import DatabaseConfig
from database.vector_db import VectorDatabase
import httpx
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title # 제목 추출

router = APIRouter()

# MySQL 데이터베이스 설정
db_config = DatabaseConfig()
db = db_config.get_db()

class ImageEmbRequest(BaseModel):
    url: str
    type: str = "image"
    date: str

@router.post("/image_embedding")
async def get_image_embedding_endpoint(request: ImageEmbRequest):
    try:
        # 이미지 캡셔닝 및 텍스트 생성
        caption = await imagecaption(request.url)
        
        # 번역 텍스트 생성
        transcaption = await translate_text(caption)
        
        # E5 모델을 사용하여 번역된 한글 텍스트 임베딩
        embedding = await embed_text(transcaption)

        # 데이터베이스에 결과 저장 (번역된 한국어 캡셔닝만 저장)
        image_id = db.insert_image(request.url, transcaption)

        summary_text = await generate_summary(transcaption)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)

        # 결과 준비
        results = {
            "success": True,
            "image_url": request.url,
            "original_caption": caption,
            "title": show_title,
            "요약": summary_text,
            "keyword": keyword,
            "translated_caption": transcaption,
            "텍스트 임베딩값": embedding
        }

        payload = {
            "id": str(image_id),
            "embedding": embedding,
            "link": request.url,
            "type": request.type,
            "date": request.date,
            "summary": str(summary_text),
            "keyword" : str(keyword),
            "title" : str(show_title)
        }

        spring_url = "http://localhost:8080/api/embedding"
        async with httpx.AsyncClient() as client:
            try:
                spring_response = await client.post(spring_url, json=payload)
                spring_response.raise_for_status()
                # Spring 응답 본문 출력 (문자열로 변환하여 출력)
                spring_response_text = spring_response.text
                print(f"Spring Boot 서버로부터의 응답: {spring_response_text}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"스프링 서버와 연결 중 HTTP 오류가 발생했습니다. 오류 메시지: {str(e)}")
            except httpx.RequestError as e:
                print(f"Request error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"스프링 서버와 연결 중 요청 오류가 발생했습니다. 오류 메시지: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"스프링 서버와 연결 중 예기치 못한 오류가 발생했습니다. 오류 메시지: {str(e)}")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    print("모든 처리 완료")
    return results
