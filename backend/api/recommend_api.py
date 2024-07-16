from fastapi import APIRouter, HTTPException
import openai
from dotenv import load_dotenv
import os
from database.vector_db import VectorDatabase

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 벡터 데이터베이스 설정
vector_db = VectorDatabase(
    api_key="a662c43c-d2dd-4e2d-b187-604b1cf9414c",
    environment="us-east-1",
    index_name="dlrunner",
    dimension=384
)

# 사용자의 최근 북마크를 기반으로 관심사 추천 기능
@router.get("/recommend")
async def get_recommend():
    try:
        # 모든 북마크 데이터를 가져옵니다.
        response = vector_db.query_by_metadata({})
        if not response or not response["matches"]:
            print("No bookmarks found")
            return {"recommendations": []}

        recent_bookmarks = [
            {"link": item["metadata"]["link"], "summary": item["metadata"]["summary"]}
            for item in response["matches"]
        ]
        print(f"Recent bookmarks: {recent_bookmarks}")

        # 각 북마크의 요약을 기반으로 추천을 생성합니다.
        recommendations = []
        for bookmark in recent_bookmarks:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 조수입니다."},
                    {"role": "user", "content": f"이 사용자는 다음 내용을 북마크했습니다: {bookmark['summary']}.이 사용자가 관심있을 만한 주제를 추천해주세요 그 주제에 맞는 한국에서 서비스하는 홈페이지를 추천해줘 길지않게 3줄로 알려주세요."}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            recommendations.append({"link": bookmark["link"], "recommendation": response.choices[0].message['content'].strip()})

        print(f"Recommendations: {recommendations}")
        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")