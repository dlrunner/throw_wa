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

index_name = 'dlrunner'

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
                    "type": match['metadata']['type'] if 'matadata' in match else {},
                    "title": match['metadata']['title'] if 'metadata' in match and 'title' in match['metadata'] else None
                })

            if len(unique_matches) >= request.top_k:
                break

        return {
            "matches": unique_matches
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

