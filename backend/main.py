import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import numpy as np
from api.youtube_link_api import router as youtube_router
from api.pdf_link_api import router as pdf_router
from api.crawler_link_api import router as crawler_router

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(youtube_router, prefix="/api")
app.include_router(pdf_router, prefix="/api")
app.include_router(crawler_router, prefix="/api")

# 앱 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
