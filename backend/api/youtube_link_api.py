from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import yt_dlp
import whisper
import os
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from transformers import AutoModel, AutoTokenizer
import torch
from database.database import Database
from database.vector_db import VectorDatabase
import httpx
from models.embedding import embed_text  # 임베딩 함수 호출

router = APIRouter()

class TranscribeRequest(BaseModel):
    url: str
    language: str = "ko"

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

# 유튜브 오디오 다운로드 함수 pip install yt_dlp 설치 필요
def download_audio(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print(f"Downloaded audio to {output_path}")

# 오디오 -> 텍스트 추출 pip install openai-whisper 설치 필요
def transcribe_audio(audio_path, language="ko"):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, language=language)
    return result["text"]

# 다운 받은 오디오 파일을 복사 후 mp3형태로 whisper로 텍스트 추출후 복사 된 파일 삭제 내용은 디비에 저장
def process_youtube_link(youtube_url, language="ko"):
    audio_path = "temp_audio"
    actual_audio_path = audio_path + ".mp3"
    
    download_audio(youtube_url, audio_path)
    
    if not os.path.exists(actual_audio_path):
        raise FileNotFoundError(f"Audio file not found: {actual_audio_path}")
    
    content = transcribe_audio(actual_audio_path, language)
    
    os.remove(actual_audio_path)
    
    # MySQL에 링크와 전사 텍스트 저장
    video_id = db.insert_video(youtube_url, content)

    return content, video_id

# 엔드포인트
@router.post("/youtube_text")
async def transcribe(request: TranscribeRequest):
    try:
        result, video_id = process_youtube_link(request.url, request.language)
        embedding = embed_text(result)

        payload = {
        "id": str(id),
        "embedding" : embedding,
        "link" : request.url
    }

        spring_url = "http://localhost:8080/api/embedding"
        async with httpx.AsyncClient() as client:
            try:
                spring_response = await client.post(spring_url, json=payload)
                spring_response.raise_for_status()
                print(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to Spring Boot server: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결할 수 없습니다.")
            
        return {
            "success": True,
            "content": result,
            "video_id": video_id,
            "embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# call_youtube 엔드포인트
async def call_youtube(link: str):
    request = TranscribeRequest(url=link)
    return await transcribe(request)
