from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
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

index_name = 'dlrunner'

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

# 텍스트 임베딩 모델
model_name = "intfloat/multilingual-e5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    # 텍스트를 최대 길이 77로 분할
    max_length = 77
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    embeddings = []
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
            # BERT 모델의 출력에서 문장 임베딩을 생성 (평균 풀링)
            text_features = outputs.last_hidden_state.mean(dim=1)
        embeddings.append(text_features.squeeze().cpu().numpy())
    
    # 모든 청크 임베딩의 평균을 계산
    mean_embedding = np.mean(embeddings, axis=0)
    return mean_embedding.tolist()

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

