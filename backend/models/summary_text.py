import openai
import os

# ChatGPT를 사용한 요약 함수
async def generate_summary(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키를 가져옴
    response = await openai.Completion.acreate(
        model="gpt-4",
        prompt=f"다음 텍스트를 요약해 주세요: {text}",
        max_tokens=100,
    )
    return response.choices[0].text.strip()
