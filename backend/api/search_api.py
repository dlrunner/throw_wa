from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
import pinecone
import numpy as np
from models.embedding import embed_text  # 임베딩 함수 호출
import os

class QueryRequest(BaseModel):
    text: str
    top_k: int = 6

router = APIRouter()

# Pinecone 초기화
pc = pinecone.Pinecone(
    api_key= os.getenv("PINECONE_API_KEY")
)

# 환경 변수 사용
spring_api_url = os.getenv("SPRING_API_URL")

index_name = 'throw-wa'

index = pc.Index(index_name)


@router.post("/search")
async def search(request: QueryRequest):
    try:
        query_vector = embed_text(request.text) # 텍스트임베딩 호출

        result = index.query(
            vector=query_vector,
              top_k=request.top_k * 2,
              include_metadata=True
            )
        
        unique_links =set()
        unique_matches = []

        for match in result['matches']:
            link = match['metadata']['link'] if 'metadata' in match and 'link' in match['metadata'] else None
            if link and link not in unique_links:
                unique_links.add(link)
                unique_matches.append({
                    "id": match['id'],
                    "score": match['score'],
                    "link": link,
                    "summary": match['metadata']['summary'],
                    "keyword": match['metadata']['keyword'],
                    "type": match['metadata']['type'],
                    "title": match['metadata']['title'] if 'metadata' in match and 'title' in match['metadata'] else None,
                    "s3OriginalFilename": match['metadata']['s3OriginalFilename'] if 'metadata' in match and 's3OriginalFilename' in match['metadata'] else None,
                    "s3Key": match['metadata']['s3Key'] if 'metadata' in match and 's3Key' in match['metadata'] else None,
                    "s3Url": match['metadata']['s3Url'] if 'metadata' in match and 's3Url' in match['metadata'] else None
                })

            if len(unique_matches) >= request.top_k:
                break

        return {
            "matches": unique_matches
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

