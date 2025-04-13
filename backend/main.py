from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from modules.youtube import YouTubeAPI
from modules.evaluator import ContentEvaluator

# 환경 변수 로드
load_dotenv(os.path.join("credentials", ".env"))

app = FastAPI(
    title="CTS API",
    description="Content Trust Score API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 인스턴스 생성
youtube_api = YouTubeAPI()
evaluator = ContentEvaluator()

@app.get("/")
async def root():
    return {"message": "CTS API 서버가 실행 중입니다."}

@app.get("/env-check")
async def env_check():
    return {
        "youtube_api_key": bool(os.getenv("YOUTUBE_API_KEY")),
        "redis_host": os.getenv("REDIS_HOST", "redis"),
        "redis_port": os.getenv("REDIS_PORT", 6379)
    }

@app.get("/youtube/video/{video_id}")
async def get_video_info(video_id: str):
    return youtube_api.get_video_info(video_id)

@app.get("/youtube/search")
async def search_videos(query: str, max_results: int = 10):
    return youtube_api.search_videos(query, max_results)

@app.get("/evaluate/{video_id}")
async def evaluate_video(video_id: str):
    """
    비디오의 신뢰도를 평가합니다.
    """
    try:
        # 비디오 정보 가져오기
        video_info = youtube_api.get_video_info(video_id)
        if "error" in video_info:
            return video_info
        
        # 신뢰도 평가
        evaluation = evaluator.evaluate(video_info)
        return evaluation
        
    except Exception as e:
        return {"error": f"평가 중 오류 발생: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 