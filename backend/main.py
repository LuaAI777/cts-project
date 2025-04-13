from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from modules.youtube import YouTubeAPI
from modules.evaluator import Evaluator
from datetime import datetime, timedelta
import json
from jose import JWTError, jwt
from passlib.context import CryptContext

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

# 관리자 설정 모델
class AdminConfig(BaseModel):
    weights: Dict[str, float]
    thresholds: Dict[str, Dict[str, int]]
    keywords: Dict[str, List[str]]

# 관리자 히스토리 모델
class ConfigHistory(BaseModel):
    timestamp: datetime
    changes: str
    user: str

# 관리자 설정 저장소
admin_config = {
    "weights": {
        "source": 0.6,
        "content": 0.4
    },
    "thresholds": {
        "subscribers": {
            "high": 1000000,
            "medium": 100000,
            "low": 10000
        },
        "activity": {
            "high": 365,
            "medium": 180,
            "low": 90
        }
    },
    "keywords": {
        "required": ["연구", "데이터", "출처"],
        "suspicious": ["확실", "무조건", "100%"]
    }
}

# 설정 변경 히스토리
config_history = []

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 사용자 모델
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = False
    role: str = "user"

class UserInDB(User):
    hashed_password: str

# 사용자 데이터베이스 (실제 구현에서는 DB 사용)
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "disabled": False,
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123")
    }
}

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 사용자 인증
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

# 관리자 권한 확인
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# 로그인 엔드포인트
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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

# 관리자 API 엔드포인트
@app.get("/api/admin/config")
async def get_admin_config(current_user: User = Depends(get_current_admin_user)):
    return admin_config

@app.post("/api/admin/config")
async def update_admin_config(
    config: AdminConfig,
    current_user: User = Depends(get_current_admin_user)
):
    global admin_config, config_history
    
    # 변경 내용 추적
    changes = []
    for key, value in config.dict().items():
        if json.dumps(admin_config[key]) != json.dumps(value):
            changes.append(f"{key} 변경됨")
    
    if changes:
        # 히스토리 추가
        config_history.append({
            "timestamp": datetime.now(),
            "changes": ", ".join(changes),
            "user": current_user.username
        })
        
        # 설정 업데이트
        admin_config = config.dict()
        
        return {"message": "설정이 업데이트되었습니다."}
    else:
        return {"message": "변경된 설정이 없습니다."}

@app.get("/api/admin/history")
async def get_config_history(current_user: User = Depends(get_current_admin_user)):
    return config_history

# 설정 변경 승인 프로세스
pending_changes = []

@app.post("/api/admin/config/pending")
async def submit_pending_changes(
    config: AdminConfig,
    current_user: User = Depends(get_current_admin_user)
):
    pending_changes.append({
        "config": config.dict(),
        "submitted_by": current_user.username,
        "submitted_at": datetime.now(),
        "status": "pending"
    })
    return {"message": "변경 요청이 제출되었습니다."}

@app.post("/api/admin/config/approve/{change_id}")
async def approve_changes(
    change_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    if 0 <= change_id < len(pending_changes):
        change = pending_changes[change_id]
        if change["status"] == "pending":
            # 설정 업데이트
            global admin_config
            admin_config = change["config"]
            
            # 히스토리 추가
            config_history.append({
                "timestamp": datetime.now(),
                "changes": "승인된 변경 적용",
                "user": current_user.username
            })
            
            # 상태 업데이트
            change["status"] = "approved"
            change["approved_by"] = current_user.username
            change["approved_at"] = datetime.now()
            
            return {"message": "변경이 승인되었습니다."}
    raise HTTPException(status_code=404, detail="변경 요청을 찾을 수 없습니다.")

# 설정 롤백 기능
@app.post("/api/admin/config/rollback/{history_id}")
async def rollback_changes(
    history_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    if 0 <= history_id < len(config_history):
        # 이전 설정으로 롤백
        global admin_config
        admin_config = config_history[history_id]["config"]
        
        # 히스토리 추가
        config_history.append({
            "timestamp": datetime.now(),
            "changes": f"롤백: {config_history[history_id]['changes']}",
            "user": current_user.username
        })
        
        return {"message": "설정이 롤백되었습니다."}
    raise HTTPException(status_code=404, detail="히스토리를 찾을 수 없습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 