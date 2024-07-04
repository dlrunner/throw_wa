from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image
import requests
from io import BytesIO
from database.database import Database

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

# CLIP 모델 및 프로세서 로드
clip_model_name = "openai/clip-vit-large-patch14"
clip_model = CLIPModel.from_pretrained(clip_model_name)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)

# 이미지 캡셔닝 모델 및 프로세서 로드
blip_model_name = "Salesforce/blip-image-captioning-base"
blip_processor = BlipProcessor.from_pretrained(blip_model_name)
blip_model = BlipForConditionalGeneration.from_pretrained(blip_model_name)

class ImageEmbRequest(BaseModel):
    image_url: str
    candidate_labels: list[str] = []

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
        
        # 입력 데이터 전처리
        clip_inputs = clip_processor(text=[caption], images=[image], return_tensors="pt", padding=True)

        # 모델 예측
        with torch.no_grad():
            outputs = clip_model(**clip_inputs)

        # 텍스트 및 이미지 임베딩 추출
        text_embeds = outputs.text_embeds
        image_embeds = outputs.image_embeds

        # 유사도 계산
        similarity = torch.nn.functional.cosine_similarity(image_embeds, text_embeds)

        # 이미지 임베딩
        image_embedding = image_embeds.squeeze().numpy().tolist()

        # 가장 유사한 텍스트와 점수
        best_label = caption
        best_score = similarity.item()

        # 각 레이블에 대한 유사도 점수 딕셔너리 생성
        label_similarities = {caption: best_score}

        # 데이터베이스에 결과 저장
        db.insert_image(request.image_url, caption)

        # 결과 준비
        results = {
            "image_url": request.image_url,
            "best_label": best_label,
            "best_score": best_score,
            "label_similarities": label_similarities,
            "image_embedding": image_embedding
        }

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
