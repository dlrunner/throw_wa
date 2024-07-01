from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import yt_dlp
import whisper
import os
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from database import Database

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

# # Faiss 벡터 데이터베이스 초기화
# dimension = 384  # sentence-transformers 'distiluse-base-multilingual-cased-v1' 모델의 임베딩 차원
# index = faiss.IndexFlatL2(dimension)

# # 임베딩 모델 로드
# model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

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

def transcribe_audio(audio_path, language="ko"):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, language=language)
    return result["text"]

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

    # # 전사 텍스트를 임베딩하여 Faiss에 저장
    # embedding = model.encode([transcription])[0]
    # index.add(np.array([embedding]))

    return content, video_id

@router.post("/youtube_text")
async def transcribe(request: TranscribeRequest):
    try:
        result, video_id = process_youtube_link(request.url, request.language)
        return {"success": True, "content": result, "video_id": video_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))