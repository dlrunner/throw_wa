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
        model="gpt-4o-mini",  # ChatGPT 모델 사용
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"다음 텍스트를 다음 카테고리 중 하나로 분류해주세요: IT 지식, 음식, 여행, 교육, 건강, 금융, 동물, 정치, 지식, 예능, 스포츠, 기타. 분류 결과만 답변해주세요.: {text}"}
        ],
        max_tokens=10,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

