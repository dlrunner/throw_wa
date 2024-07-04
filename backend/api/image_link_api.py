from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image
import requests
from io import BytesIO
from database.database import Database
from database.vector_db import VectorDatabase
import numpy as np
from googletrans import Translator

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

# 백터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="vector",
    dimension=768
)

# CLIP 모델 및 프로세서 로드
clip_model_name = "openai/clip-vit-large-patch14"
clip_model = CLIPModel.from_pretrained(clip_model_name)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)

# 이미지 캡셔닝 모델 및 프로세서 로드
blip_model_name = "Salesforce/blip-image-captioning-base"
blip_processor = BlipProcessor.from_pretrained(blip_model_name)
blip_model = BlipForConditionalGeneration.from_pretrained(blip_model_name)

# 번역기 초기화
translator = Translator()

class ImageEmbRequest(BaseModel):
    image_url: str
    
@router.post("/image_embedding")
async def get_image_embedding(request: ImageEmbRequest):
    try:
        # 이미지 URL에서 이미지 로드
        response = requests.get(request.image_url)
        image = Image.open(BytesIO(response.content))

        # 이미지 캡셔닝
        blip_inputs = blip_processor(image, return_tensors="pt")
        caption_ids = blip_model.generate(**blip_inputs)
        caption = blip_processor.batch_decode(caption_ids, skip_special_tokens=True)[0]

        # 캡션 번역
        translated_caption = translator.translate(caption, dest='ko').text

        # CLIP을 사용한 이미지 임베딩
        clip_image_inputs = clip_processor(images=[image], return_tensors="pt", padding=True)
        with torch.no_grad():
            clip_image_outputs = clip_model.get_image_features(**clip_image_inputs)
        image_embedding = clip_image_outputs.squeeze().cpu().numpy()

        # CLIP을 사용한 텍스트 임베딩 (번역된 캡션 사용)
        clip_text_inputs = clip_processor(text=[translated_caption], return_tensors="pt", padding=True)
        with torch.no_grad():
            clip_text_outputs = clip_model.get_text_features(**clip_text_inputs)
        text_embedding = clip_text_outputs.squeeze().cpu().numpy()

        # 유사도 계산 (numpy를 사용하여 계산)
        similarity = np.dot(image_embedding, text_embedding) / (np.linalg.norm(image_embedding) * np.linalg.norm(text_embedding))

        # 데이터베이스에 결과 저장
        image_id = db.insert_image(request.image_url, translated_caption)

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=str(image_id),
            vector=text_embedding,
            metadata={"link": request.image_url}
        )

        # 결과 준비
        results = {
            "image_url": request.image_url,
            "이미지 캡셔닝 결과 (영어)": caption,
            "이미지 캡셔닝 결과 (한글)": translated_caption,
            "이미지-텍스트 유사도": float(similarity),
            "이미지 임베딩값": image_embedding.tolist(),
            "텍스트 임베딩값": text_embedding.tolist()
        }

        print("모든 처리 완료")
        return results
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
