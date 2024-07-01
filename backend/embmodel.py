from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# BERT 모델과 토크나이저 로드
model_name = "klue/bert-base"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# 텍스트 토크나이즈
text = "이 문장은 한국어로 작성되었습니다."
inputs = tokenizer(text, return_tensors='pt')

# 모델 예측
with torch.no_grad():
    outputs = model(**inputs)

# 텍스트 임베딩 추출
# outputs.last_hidden_state는 (batch_size, sequence_length, hidden_size) 형태의 텐서
embeddings = outputs.last_hidden_state

# 첫 번째 토큰에 대한 임베딩 벡터 출력 (예: [CLS] 토큰)
cls_embedding = embeddings[0, 0, :].numpy()
print("CLS 토큰 임베딩 벡터:", cls_embedding)

# ---------------------------------------------------------------------

# 예시 문서 임베딩 벡터 (미리 계산된 벡터)
document_embeddings = np.random.randn(100, 768)  # 100개의 문서, 768차원 벡터

# 쿼리 텍스트 임베딩 벡터 (미리 계산된 벡터)
query_embedding = cls_embedding  # 이전에 계산된 BERT CLS 임베딩 벡터

# 유사도 계산
similarities = cosine_similarity([query_embedding], document_embeddings)

# 유사도가 가장 높은 문서 인덱스 찾기
most_similar_idx = similarities.argmax()
print(f"가장 유사한 문서 인덱스: {most_similar_idx}")
print("유사도 점수:", similarities)

# ---------------------------------------------------------------------

# 데이터 임베딩 벡터 (다시 생성, PCA 시각화 위해)
document_embeddings = np.random.randn(100, 768)  # 100개의 문서, 768차원 벡터

# 차원 축소
pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(document_embeddings)

# 시각화
plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1])
plt.title("PCA로 시각화한 임베딩 벡터")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.show()
