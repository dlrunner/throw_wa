# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
# import torch
# from PIL import Image
# import requests
# from io import BytesIO
# from database.database import Database
# from database.vector_db import VectorDatabase
# import numpy as np
# from googletrans import Translator

# router = APIRouter()

# # MySQL 데이터베이스 연결 설정
# db_config = {
#     'host': '127.0.0.1',
#     'user': 'nlrunner',
#     'password': 'nlrunner',
#     'database': 'nlrunner_db'
# }
# db = Database(**db_config)
# db.connect()
# db.create_table()

# # 백터 데이터베이스 설정
# vector_db = VectorDatabase(
#     api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
#     environment="us-east-1",
#     index_name="vector",
#     dimension=384  # intfloat/multilingual-e5-small 임베딩 벡터의 차원
# )

# # 텍스트 임베딩 모델
# model_name = "intfloat/multilingual-e5-small"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModel.from_pretrained(model_name)

# # 모델을 CPU로 설정
# device = torch.device("cpu")
# model.to(device)

# # 이미지 캡셔닝 모델 및 프로세서 로드
# florence_model_name = "microsoft/Florence-2-base"
# florence_tokenizer = AutoTokenizer.from_pretrained(florence_model_name, trust_remote_code=True)
# florence_model = AutoModelForCausalLM.from_pretrained(florence_model_name, trust_remote_code=True)
# florence_model.to(device)  # 모델을 CPU로 설정

# # 번역기 초기화
# translator = Translator()

# class ImageEmbRequest(BaseModel):
#     image_url: str

# @router.post("/image_embedding")
# async def get_image_embedding(request: ImageEmbRequest):
#     try:
#         # 이미지 URL에서 이미지 로드
#         response = requests.get(request.image_url)
#         image = Image.open(BytesIO(response.content))

#         # 이미지 캡셔닝
#         inputs = florence_tokenizer(images=image, return_tensors="pt").to(device)
#         with torch.no_grad():
#             outputs = florence_model.generate(**inputs)
#         caption = florence_tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

#         # 캡션 번역
#         translated_caption = translator.translate(caption, dest='ko').text

#         # 이미지 임베딩 (임시로 임베딩을 생성하는 부분, 실제로는 올바른 임베딩 생성 코드 필요)
#         image_embedding = np.random.rand(384)

#         # 텍스트 임베딩 (번역된 캡션 사용)
#         text_inputs = tokenizer(text=[translated_caption], return_tensors="pt", padding=True).to(device)
#         with torch.no_grad():
#             text_outputs = model(**text_inputs)
#         text_embedding = text_outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

#         # 유사도 계산 (numpy를 사용하여 계산)
#         similarity = np.dot(image_embedding, text_embedding) / (np.linalg.norm(image_embedding) * np.linalg.norm(text_embedding))

#         # 데이터베이스에 결과 저장
#         image_id = db.insert_image(request.image_url, translated_caption)

#         # 벡터 디비에 upsert
#         vector_db.upsert_vector(
#             vector_id=str(image_id),
#             vector=text_embedding,
#             metadata={"link": request.image_url}
#         )

#         # 결과 준비
#         results = {
#             "image_url": request.image_url,
#             "이미지 캡셔닝 결과 (영어)": caption,
#             "이미지 캡셔닝 결과 (한글)": translated_caption,
#             "이미지-텍스트 유사도": float(similarity),
#             "이미지 임베딩값": image_embedding.tolist(),
#             "텍스트 임베딩값": text_embedding.tolist()
#         }

#         print("모든 처리 완료")
#         return results
#     except Exception as e:
#         print(f"오류 발생: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
