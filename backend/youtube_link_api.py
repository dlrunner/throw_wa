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
from transformers import BertTokenizer, BertModel, AutoModel, AutoTokenizer
import torch

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

# 오디오 -> 텍스트 추출 pip install openai-whiper 설치 필요
def transcribe_audio(audio_path, language="ko"):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, language=language)
    return result["text"]

# 다운 받은 오디오 파일을 복사 후 mp3형태로 whiper로 텍스트 추출후 복사 된 파일 삭제 내용은 디비에 저장
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

# 임베딩 함수
def embed_text(text: str) -> list :
    tokenizer = AutoTokenizer.from_pretrained('klue/bert-base') # 모델은 transformers의 klue/bert-base 영어 한국어 지원 모델
    model = AutoModel.from_pretrained('klue/bert-base')         # pip install transformers torch 설치 필요

    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    embeddings = torch.mean(outputs.last_hidden_state, dim=1)
    return embeddings.detach().numpy().tolist()



@router.post("/youtube_text")
async def transcribe(request: TranscribeRequest):
    try:
        result, video_id = process_youtube_link(request.url, request.language)
        embedding = embed_text(result)
        return {"success": True, "content": result, "video_id": video_id, "embedding" : embedding}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))