import os
from dotenv import load_dotenv
import openai

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
openai_api_key = os.getenv("OPENAI_API_KEY")

# ChatGPT를 사용한 키워드 추출 함수
async def keyword_extraction(text):
    openai.api_key = openai_api_key  # 환경 변수에서 API 키를 가져옴
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",  # ChatGPT 모델 사용
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"다음 텍스트에서 가장 중요하다고 생각하는 키워드 하나만 추출해주세요. 가능한 한 단어로 간결하게 작성해주세요: {text}"}
        ],
        max_tokens=10,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# 예시: .env 파일에서 불러온 API 키 출력 (디버깅용)
print(f"제대로 오는지 확인: {openai_api_key}")
