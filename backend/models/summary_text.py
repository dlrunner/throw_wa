import os
from dotenv import load_dotenv
import openai

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
openai_api_key = os.getenv("OPENAI_API_KEY")

# ChatGPT를 사용한 요약 함수
async def generate_summary(text):
    openai.api_key = openai_api_key  # 환경 변수에서 API 키를 가져옴
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",  # ChatGPT 모델 사용
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"다음 텍스트를 3줄로 요약해 주세요. 각 요약 항목은 줄바꿈으로 구분되어야 합니다. 1. 2. 3. 이렇게 요약해 주세요: {text}"}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

