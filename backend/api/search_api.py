from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from transformers import CLIPProcessor, CLIPModel
import torch
import pinecone
import numpy as np

class QueryRequest(BaseModel):
    text: str
    top_k: int = 6

router = APIRouter()

# Pinecone 초기화
pc = pinecone.Pinecone(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c"
)

index_name = 'vector'

# 인덱스가 없는 경우 생성
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # clip 임베딩 벡터의 차원
        metric='cosine',  # 유사도 측정 방법
        spec=pinecone.ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )

index = pc.Index(index_name)

# CLIP 모델 및 프로세서 로드
clip_model_name = "openai/clip-vit-large-patch14"
clip_model = CLIPModel.from_pretrained(clip_model_name)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)

# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = clip_model.get_text_features(**inputs)
    embedding = text_features.squeeze().cpu().numpy().tolist()
    return embedding

@router.post("/search")
async def search(request: QueryRequest):
    try:
        query_vector = embed_text(request.text)

        result = index.query(
            vector=query_vector,
              top_k=request.top_k,
              include_metadata=True
            )

        return {
            "matches": [
                {
                    "id": match['id'], 
                    "유사도": match['score'],
                    "링크": match['metadata'] if 'metadata' in match else {}
                }
                for match in result['matches']
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

