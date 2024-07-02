import torch
from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model

# KoBERT 모델과 토크나이저 로드
model, vocab = get_pytorch_kobert_model()
tokenizer = get_tokenizer()

# 텍스트 예시
text = "한국어 BERT 모델을 사용하여 텍스트를 임베딩합니다."

# 토큰화
tokens = tokenizer.tokenize(text)
token_ids = vocab.convert_tokens_to_ids(tokens)
token_ids = torch.tensor([token_ids])

# 임베딩 생성
with torch.no_grad():
    all_encoder_layers, pooled_output = model(token_ids)

# 문장 임베딩 (pooled output)
sentence_embedding = pooled_output

print(sentence_embedding.shape)  # 임베딩 차원 출력
print(sentence_embedding)  # 임베딩 벡터 출력