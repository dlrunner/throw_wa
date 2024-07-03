import torch
from transformers import CLIPProcessor, CLIPModel
import requests
from bs4 import BeautifulSoup

# 모델 및 프로세서 로드
model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# 웹페이지 크롤링 함수
def crawl_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 네이버 블로그의 본문 내용 추출 (p 태그만)
    content = soup.find('div', class_='se-main-container')
    if content:
        paragraphs = content.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs])
    else:
        text = soup.get_text()  # fallback: 전체 텍스트 추출
    
    return text

# 텍스트 임베딩 생성 함수
def get_text_embeddings(texts, batch_size=32):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = processor(text=batch, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model.get_text_features(**inputs)
        embeddings.append(outputs)
    return torch.cat(embeddings)

# URL 크롤링
url = "https://m.blog.naver.com/limitsinx/221598890687"
crawled_text = crawl_webpage(url)

# 크롤링한 텍스트를 문장 단위로 분리 (간단한 방법 사용)
sentences = crawled_text.split('.')
sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

# 임베딩 생성
text_embeddings = get_text_embeddings(sentences)

print(f"크롤링한 텍스트의 문장 수: {len(sentences)}")
print(f"생성된 임베딩 shape: {text_embeddings.shape}")
print("\n")

# 모든 문장 결과 출력
print("크롤링한 모든 문장 결과:")
for i, sentence in enumerate(sentences, 1):
    print(f"문장 {i}: {sentence}")
print("\n")

# 임베딩 결과 출력 (처음 5개 문장에 대해서만)
print("임베딩 결과 (처음 5개 문장, 각 10개 차원):")
for i in range(min(5, len(sentences))):
    print(f"문장 {i+1} 임베딩: {text_embeddings[i][:10].tolist()}")