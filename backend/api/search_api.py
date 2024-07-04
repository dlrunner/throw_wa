from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
import pinecone
import numpy as np

class QueryRequest(BaseModel):
    text: str
    top_k: int = 3

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
        dimension=768,  # BERT 임베딩 벡터의 차원
        metric='cosine',  # 유사도 측정 방법
        spec=pinecone.ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )

index = pc.Index(index_name)

# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    tokenizer = AutoTokenizer.from_pretrained('klue/bert-base')
    model = AutoModel.from_pretrained('klue/bert-base')
    
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    
    embeddings = torch.mean(outputs.last_hidden_state, dim=1).squeeze().detach().numpy().astype(np.float32).tolist()
    return embeddings

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

