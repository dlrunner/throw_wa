from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, APIRouter
from database.vector_db import VectorDatabase
import numpy as np
import os

router = APIRouter()

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key= os.getenv("PINECONE_API_KEY"),
    environment="us-east-1",
    index_name="throw-wa",
    dimension=384
)

user_db = VectorDatabase(
    api_key= os.getenv("PINECONE_API_KEY"),
    environment="us-east-1",
    index_name="throw-wa-user",
    dimension=384
)

class VectorUpsertRequest(BaseModel):
    id: str
    embedding: list[float]
    link: str
    type: str # 유튜브인지 웹인지 pdf인지 파악하기 위한 용도
    date: str # 링크 업로드 날짜 
    summary : str # 요약 메타데이터 선언
    keyword : str # 키워드 메타데이터
    title : str # 제목 메타데이터
    userId: str # 로그인 유저 식별값 메타데이터
    userName: str # 로그인 유저 이름 메타데이터

class VectorS3UpsertRequest(BaseModel):
    id: str
    embedding: list[float]
    link: str
    type: str # 유튜브인지 웹인지 pdf인지 파악하기 위한 용도
    date: str # 링크 업로드 날짜 
    summary : str # 요약 메타데이터 선언
    keyword : str # 키워드 메타데이터
    title : str # 제목 메타데이터
    s3OriginalFilename : str # s3 OriginalFilename 메타데이터
    s3Key : str # s3 key 메타데이터
    s3Url : str # s3 url 메타데이터
    userId: str # 로그인 유저 식별값 메타데이터
    userName: str # 로그인 유저 이름 메타데이터

class SignUpRequest(BaseModel):
    id: str
    email: str
    password: str
    name: str
    type : str
    role : str

@router.post("/vector_upsert")
async def vector_upsert(request: VectorUpsertRequest):
    try:

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=request.id,
            vector=request.embedding,
            metadata={
                "link": request.link,
                "type": request.type,
                "date": request.date,
                "summary" : request.summary,
                "keyword" : request.keyword,
                "title" : request.title,
                "userId": request.userId,
                "userName": request.userName
                }
        )

        return {"success": True}
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector_s3_upsert")
async def vector_upsert_s3(request: VectorS3UpsertRequest):
    try:

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=request.id,
            vector=request.embedding,
            metadata={
                "link": request.link,
                "type": request.type,
                "date": request.date,
                "summary" : request.summary,
                "keyword" : request.keyword,
                "title" : request.title,
                "s3OriginalFilename" : request.s3OriginalFilename,
                "s3Key" : request.s3Key,
                "s3Url" : request.s3Url,
                "userId": request.userId,
                "userName": request.userName
                }
        )

        return {"success": True}
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/signup_upsert")
async def sign_up(request: SignUpRequest):
    try:

        # 유저 디비에 upsert
        user_db.upsert_vector(
            vector_id=request.id,
            metadata={
                "email" : request.email,
                "password" : request.password,
                "name" : request.name,
                "type" : request.type,
                "role" : request.role
                }
        )

        return {"success": True}
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
