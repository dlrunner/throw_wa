import torch
from PIL import Image
import requests
import matplotlib.pyplot as plt
from transformers import CLIPProcessor, CLIPModel

# CLIP 모델 및 프로세서 로드
model_name = "openai/clip-vit-large-patch14-336"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# 이미지 URL 및 로드
image_url = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
image = Image.open(requests.get(image_url, stream=True).raw)

# 이미지 전처리
inputs = processor(images=image, return_tensors="pt")

# 이미지 임베딩 생성
with torch.no_grad():
    image_features = model.get_image_features(**inputs)

# 임베딩 정보 출력
print("이미지 임베딩 shape:", image_features.shape)
print("이미지 임베딩 (처음 5개 값):", image_features[0, :5].tolist())

# 이미지 임베딩 시각화
plt.figure(figsize=(10, 5))
plt.imshow(image_features.numpy().reshape(-1, 16), cmap='viridis', aspect='auto')
plt.colorbar()
plt.title("Image Embedding Visualization")
plt.xlabel("Embedding Dimensions")
plt.ylabel("Flattened Embedding")
plt.show()

# 원본 이미지 표시
plt.figure(figsize=(8, 8))
plt.imshow(image)
plt.axis('off')
plt.title("Original Image")
plt.show()

# 임베딩 정규화 (선택적)
normalized_embedding = torch.nn.functional.normalize(image_features, p=2, dim=1)
print("정규화된 임베딩 (처음 5개 값):", normalized_embedding[0, :5].tolist())