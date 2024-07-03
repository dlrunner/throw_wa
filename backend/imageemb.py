# imageemb.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import requests
from io import BytesIO

router = APIRouter()

# CLIP 모델 및 프로세서 로드
model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

class ImageEmbRequest(BaseModel):
    image_url: str
    candidate_labels: list[str]

@router.post("/image_embedding")
async def get_image_embedding(request: ImageEmbRequest):
    try:
        # 이미지 URL에서 이미지 로드
        response = requests.get(request.image_url)
        image = Image.open(BytesIO(response.content))

        # 입력 데이터 전처리
        inputs = processor(text=request.candidate_labels, images=image, return_tensors="pt", padding=True)

        # 모델 예측
        with torch.no_grad():
            outputs = model(**inputs)

        # 텍스트 및 이미지 임베딩 추출
        text_embeds = outputs.text_embeds
        image_embeds = outputs.image_embeds

        # 유사도 계산
        similarity = torch.nn.functional.cosine_similarity(image_embeds, text_embeds)

        # 이미지 임베딩
        image_embedding = image_embeds.squeeze().numpy().tolist()

        # 결과 준비
        results = {
            "similarities": similarity.numpy().tolist(),
            "best_label": request.candidate_labels[similarity.argmax().item()],
            "best_score": similarity.max().item(),
            "image_embedding": image_embedding
        }

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
