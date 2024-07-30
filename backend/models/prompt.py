import os
from dotenv import load_dotenv
import openai
import json

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
openai_api_key = os.getenv("OPENAI_API_KEY")

text = "embedding을 하는 방법에 대한 설명입니다."

SYSTEM_PROMPT = """\
주어지는 컨텐츠로부터 요약결과, 카테고리분류, 제목생성을 수행해야 합니다.

### 요약 규칙
1. 요약 결과는 3개의 리스트로 요약해주세요.
2. 각 요약 항목은 줄바꿈으로 구분되어야 합니다.
3. 반드시 해야 할 사항은 한 문장 요약할때 앞에 - 가 들어가야 합니다.

### 카테고리 분류 규칙
1. 다음 카테고리 중 하나로 분류해주세요: IT 지식, 음식, 여행, 교육, 건강, 금융, 동물, 정치, 지식, 예능, 스포츠, 기타.

### 제목 생성 규칙
1. 주어지는 컨텐츠에 대해 대표할 수 있는 제목을 지어주세요.
2. 제목을 생성할 때 '제목:'이라는 단어를 포함하지 마세요.
3. 제목은 한국어로 작성해야 합니다.

### json 결과형식
{
    "summary": 요약결과1, 요약결과2, 요약결과3
    "category": 카테고리
    "title": 제목
}
"""

# ChatGPT를 사용한 키워드 추출 함수
async def gpt_prompt(text):
    openai.api_key = openai_api_key  # 환경 변수에서 API 키를 가져옴
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",  # ChatGPT 모델 사용
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{text}"}
        ],
        max_tokens=1000,
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    result = json.loads(response['choices'][0]['message']['content'])
    return result
