from transformers import AutoTokenizer, AutoModel
import torch

# 모델 로드
model_name = "intfloat/multilingual-e5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 임베딩 차원 확인
text = "Hello, world!"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

# 임베딩 차원 확인
embedding_dim = outputs.last_hidden_state.size(-1)
print(f"Embedding dimension: {embedding_dim}")
