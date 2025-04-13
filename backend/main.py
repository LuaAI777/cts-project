from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from modules.youtube import YouTubeAPI
from modules.evaluator import Evaluator

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
evaluator = Evaluator()

class VideoRequest(BaseModel):
    video_id: str

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10

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

@app.post("/api/search")
async def search_videos(request: SearchRequest):
    try:
        results = youtube_api.search_videos(request.query, request.max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate")
async def evaluate_video(request: VideoRequest):
    try:
        # 비디오 정보 가져오기
        video_info = youtube_api.get_video_info(request.video_id)
        
        # 신뢰도 평가
        source_trust = evaluator.evaluate_source_trust(video_info)
        content_trust = evaluator.evaluate_content_trust(video_info)
        final_score = evaluator.calculate_final_score(source_trust, content_trust)
        
        # 분석 결과 생성
        analysis = {
            "source_analysis": _generate_source_analysis(source_trust),
            "content_analysis": _generate_content_analysis(content_trust)
        }
        
        return {
            "video_info": {
                "title": video_info["title"],
                "channel": video_info["channel_title"],
                "views": video_info["views"],
                "likes": video_info["likes"],
                "comments": video_info["comments"],
                "published_at": video_info["published_at"]
            },
            "evaluation": {
                "source_trust": {
                    "score": source_trust["total_score"],
                    "details": {
                        "subscriber_score": source_trust["subscriber_score"],
                        "activity_score": source_trust["activity_score"],
                        "engagement_score": source_trust["engagement_score"]
                    }
                },
                "content_trust": {
                    "score": content_trust["total_score"],
                    "details": {
                        "title_score": content_trust["title_score"],
                        "description_score": content_trust["description_score"],
                        "sentiment_score": content_trust["sentiment_score"]
                    }
                },
                "final_score": final_score["final_score"],
                "grade": final_score["grade"]
            },
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _generate_source_analysis(source_trust: Dict) -> str:
    """출처/채널 분석 결과 생성"""
    analysis = []
    
    if source_trust["subscriber_score"] >= 0.8:
        analysis.append("채널의 구독자 수가 매우 많습니다.")
    elif source_trust["subscriber_score"] >= 0.6:
        analysis.append("채널의 구독자 수가 적절합니다.")
    else:
        analysis.append("채널의 구독자 수가 적습니다.")
    
    if source_trust["activity_score"] >= 0.8:
        analysis.append("채널의 활동 기간이 매우 깁니다.")
    elif source_trust["activity_score"] >= 0.6:
        analysis.append("채널의 활동 기간이 적절합니다.")
    else:
        analysis.append("채널의 활동 기간이 짧습니다.")
    
    if source_trust["engagement_score"] >= 0.8:
        analysis.append("시청자 참여도가 매우 높습니다.")
    elif source_trust["engagement_score"] >= 0.6:
        analysis.append("시청자 참여도가 적절합니다.")
    else:
        analysis.append("시청자 참여도가 낮습니다.")
    
    return " ".join(analysis)

def _generate_content_analysis(content_trust: Dict) -> str:
    """내용 분석 결과 생성"""
    analysis = []
    
    if content_trust["title_score"] >= 0.8:
        analysis.append("제목이 적절합니다.")
    else:
        analysis.append("제목이 너무 짧거나 길 수 있습니다.")
    
    if content_trust["description_score"] >= 0.8:
        analysis.append("설명이 충분합니다.")
    else:
        analysis.append("설명이 부족하거나 너무 깁니다.")
    
    if content_trust["sentiment_score"] >= 0.8:
        analysis.append("내용이 중립적이고 균형 잡혀 있습니다.")
    else:
        analysis.append("내용이 편향적일 수 있습니다.")
    
    return " ".join(analysis)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 