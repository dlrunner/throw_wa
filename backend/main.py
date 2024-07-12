import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import numpy as np
from api.youtube_link_api import router as youtube_router
from api.pdf_link_api import router as pdf_router
from api.crawler_link_api import router as crawler_router
from api.search_api import router as search_router
from api.image_link_api import router as image_router
from api.upsert_api import router as upsert_router

app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "chrome-extension://bhgkbbadipohilenmjoaclooofdemmke"
]

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
app.include_router(search_router, prefix="/api")
app.include_router(image_router, prefix="/api")
app.include_router(upsert_router, prefix="/api")

# 앱 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
