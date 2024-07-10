import os
from unittest.mock import patch
import requests
from PIL import Image
from io import BytesIO
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, AutoModel
from transformers.dynamic_module_utils import get_imports
import torch
import numpy as np
from database.database import Database
from database.vector_db import VectorDatabase
import httpx

router = APIRouter()

# MySQL 데이터베이스 연결 설정
db_config = {
    'host': '127.0.0.1',
    'user': 'nlrunner',
    'password': 'nlrunner',
    'database': 'nlrunner_db'
}
db = Database(**db_config)
db.connect()
db.create_table()

# 텍스트 임베딩 모델
model_name = "intfloat/multilingual-e5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 모델을 CPU로 설정
device = torch.device("cpu")
model.to(device)

# 임포트 리스트에서 flash_attn 제거
def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

# unittest.mock을 사용하여 get_imports 함수를 패치합니다.
with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
    florence_model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
    florence_processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)

florence_model.to(device)

class ImageEmbRequest(BaseModel):
    url: str

@router.post("/image_embedding")
async def get_image_embedding(request: ImageEmbRequest):
    try:
        response = requests.get(request.url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        print(f"Request error during image fetching: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 가져오는 중 오류가 발생했습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    try:
        # 이미지 캡셔닝
        prompt = "<MORE_DETAILED_CAPTION>"
        inputs = florence_processor(text=prompt, images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_ids = florence_model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=50,
                num_beams=3,
            )

        generated_text = florence_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        parsed_answer = florence_processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        caption = parsed_answer.get("<MORE_DETAILED_CAPTION>", "No caption generated")

        # 텍스트 임베딩 (원본 영어 캡션 사용)
        text_inputs = tokenizer(text=[caption], return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            text_outputs = model(**text_inputs)
        embedding = text_outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

        # 데이터베이스에 결과 저장 (원본 영어 캡션만 저장)
        id = db.insert_image(request.url, caption)

        # 결과 준비
        results = {
            "success": True,
            "image_url": request.url,
            "이미지 캡셔닝 결과": caption,
            "텍스트 임베딩값": embedding.tolist()
        }

        payload = {
            "id": str(id),
            "embedding": embedding.tolist(),
            "link": request.url
        }

        spring_url = "http://localhost:8080/api/embedding"
        async with httpx.AsyncClient() as client:
            try:
                spring_response = await client.post(spring_url, json=payload)
                spring_response.raise_for_status()
                print(f"Spring Boot 서버로의 연결이 성공하였습니다. 응답 코드: {spring_response.status_code}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결 중 HTTP 오류가 발생했습니다.")
            except httpx.RequestError as e:
                print(f"Request error: {str(e)}")
                raise HTTPException(status_code=500, detail="스프링 서버와 연결 중 요청 오류가 발생했습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    print("모든 처리 완료")
    return results
