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

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

# 텍스트 임베딩 모델
model_name = "intfloat/multilingual-e5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 모델을 CPU로 설정
device = torch.device("cpu")
model.to(device)

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("/modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
    florence_model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
    florence_processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)

florence_model.to(device)

class ImageEmbRequest(BaseModel):
    image_url: str

@router.post("/image_embedding")
async def get_image_embedding(request: ImageEmbRequest):
    try:
        # 이미지 URL에서 이미지 로드
        response = requests.get(request.image_url)
        image = Image.open(BytesIO(response.content))

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
        
        generated_text = florence_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = florence_processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        caption = parsed_answer.get("<MORE_DETAILED_CAPTION>", "No caption generated")

        # 텍스트 임베딩 (원본 영어 캡션 사용)
        text_inputs = tokenizer(text=[caption], return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            text_outputs = model(**text_inputs)
        text_embedding = text_outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

        # 데이터베이스에 결과 저장 (원본 영어 캡션만 저장)
        image_id = db.insert_image(request.image_url, caption)

        # 벡터 디비에 upsert
        vector_db.upsert_vector(
            vector_id=str(image_id),
            vector=text_embedding,
            metadata={"link": request.image_url}
        )

        # 결과 준비
        results = {
            "image_url": request.image_url,
            "이미지 캡셔닝 결과": caption,
            "텍스트 임베딩값": text_embedding.tolist()
        }

        print("모든 처리 완료")
        return results
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
