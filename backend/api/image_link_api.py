from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.embedding import imagecaption, embed_text, translate_text  # 번역 함수 수정
from database.database import Database
from database.vector_db import VectorDatabase
import httpx
from models.summary_text import generate_summary
from models.keyword_text import keyword_extraction
from models.title_generate import generate_title # 제목 추출
import os
import aiofiles # 파일 추출

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

async def download_img(img_url):
    try:
        # 파일 이름 추출 및 처리 (로컬 파일과 URL 모두에 적용)
        real_img_url = img_url.replace('%20', ' ')
        file_name = real_img_url.split('/')[-1]

        # 로컬 파일 경로인 경우
        if real_img_url.startswith('file:///') or os.path.exists(real_img_url):
            # 파일 경로에서 'file:///'를 제거
            local_path = real_img_url.replace('file:///', '')
            async with aiofiles.open(local_path, 'rb') as file:
                file_content = await file.read()
        else:
            # 웹 URL인 경우
            async with httpx.AsyncClient() as client:
                response = await client.get(real_img_url)
                response.raise_for_status()
                file_content = response.content

        # 파일 내용을 Spring Boot로 전송
        files = {'file': (file_name, file_content)}
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8080/api/upload", files=files)
            response.raise_for_status()

        # Spring Boot에서 반환한 JSON 응답을 파싱
        result = response.json()
        return result
    except httpx.HTTPError as e:
        # 다운로드 또는 업로드 실패 시 처리
        print(f"HTTP 오류 발생: {e.status_code}")
    except Exception as e:
        # 예상치 못한 오류 발생 시 처리
        print(f"오류 발생: {e}")

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

        summary_text = await generate_summary(transcaption)
        keyword = await keyword_extraction(summary_text)
        show_title = await generate_title(summary_text)

        try:
            s3_info = await download_img(request.url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"IMG 다운로드 중 오류 발생: {str(e)}")

        # 결과 준비
        results = {
            "success": True,
            "image_url": request.url,
            "original_caption": caption,
            "title": show_title,
            "요약": summary_text,
            "keyword": keyword,
            "translated_caption": transcaption,
            "텍스트 임베딩값": embedding,
            "s3OriginalFilename" : str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url'])
        }

        payload = {
            "id": str(image_id),
            "embedding": embedding,
            "link": request.url,
            "type": request.type,
            "date": request.date,
            "summary": str(summary_text),
            "keyword" : str(keyword),
            "title" : str(show_title),
            "s3OriginalFilename" : str(s3_info['originalFilename']),
            "s3Key": str(s3_info['key']),
            "s3Url": str(s3_info['url'])
        }

        spring_url = "http://localhost:8080/api/embeddingS3"
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
