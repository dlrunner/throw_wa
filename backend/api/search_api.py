from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
import pinecone
import numpy as np
from models.embedding import embed_text  # 임베딩 함수 호출

class QueryRequest(BaseModel):
    text: str
    top_k: int = 6

router = APIRouter()

# Pinecone 초기화
pc = pinecone.Pinecone(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c"
)

index_name = 'dlrunner'

# 인덱스가 없는 경우 생성
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  
        metric='cosine',  # 유사도 측정 방법
        spec=pinecone.ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )

index = pc.Index(index_name)


@router.post("/search")
async def search(request: QueryRequest):
    try:
        query_vector = embed_text(request.text) # 텍스트임베딩 호출

        result = index.query(
            vector=query_vector,
              top_k=request.top_k,
              include_metadata=True
            )

        return {
            "matches": [
                {
                    "id": match['id'], 
                    "score": match['score'],
                    "link": match['metadata']['link'] if 'metadata' in match else {},
                    "summary": match['metadata']['summary']
                }
                for match in result['matches']
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

