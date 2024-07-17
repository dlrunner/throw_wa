import os
from dotenv import load_dotenv
import openai

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
openai_api_key = os.getenv("OPENAI_API_KEY")

# ChatGPT를 사용한 요약 함수
async def generate_title(text):
    openai.api_key = openai_api_key  # 환경 변수에서 API 키를 가져옴
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",  # ChatGPT 모델 사용
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"다음 요약내용을 가지고 제목을 지어주세요. 제목을 생성할 때 '제목:'이라는 단어를 포함하지 마세요. 제목은 한국어로 작성하세요: {text}"}
        ],
        max_tokens=100,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

