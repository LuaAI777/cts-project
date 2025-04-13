from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from modules.youtube import YouTubeAPI
from modules.evaluator import Evaluator
from modules.scoring import ScoreCalculator
from datetime import datetime, timedelta
import json
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging
import redis
from uuid import uuid4
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv(".env")

# Redis 연결 설정
def get_redis_client():
    retry = Retry(ExponentialBackoff(), 3)  # 최대 3번 재시도
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),  # 기본값을 localhost로 변경
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
        retry=retry,
        retry_on_timeout=True
    )

# Redis 연결 시도
def connect_redis(max_retries: int = 3, delay: int = 1) -> Optional[redis.Redis]:
    for attempt in range(max_retries):
        try:
            client = get_redis_client()
            client.ping()  # 연결 테스트
            logger.info("Redis 연결 성공")
            return client
        except redis.ConnectionError as e:
            logger.warning(f"Redis 연결 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # 지수 백오프
    logger.error("Redis 연결 최대 재시도 횟수 초과")
    return None

# Redis 클라이언트 초기화
redis_client = connect_redis()
if not redis_client:
    logger.warning("Redis 연결 실패. 메모리 내 데이터베이스를 사용합니다.")
    # 메모리 내 데이터베이스로 대체
    class InMemoryDB:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value):
            self.data[key] = value
        
        def exists(self, key):
            return key in self.data
        
        def rpush(self, key, value):
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)
        
        def lrange(self, key, start, end):
            if key not in self.data:
                return []
            return self.data[key][start:end]
    
    redis_client = InMemoryDB()

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
score_calculator = ScoreCalculator()

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

# Redis 키 설정
ADMIN_CONFIG_KEY = "admin:config"
CONFIG_HISTORY_KEY = "admin:history"
PENDING_CHANGES_KEY = "admin:pending"

# 초기 관리자 설정
default_admin_config = {
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

# Redis에 초기 설정 저장
if not redis_client.exists(ADMIN_CONFIG_KEY):
    redis_client.set(ADMIN_CONFIG_KEY, json.dumps(default_admin_config))

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
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return None
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
        "redis_port": os.getenv("REDIS_PORT", 6379),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/youtube/video/{video_id}")
async def get_video_info(video_id: str, current_user: Optional[User] = Depends(get_current_user)):
    try:
        video_info = youtube_api.get_video_info(video_id)
        return {
            "title": video_info["title"],
            "channelTitle": video_info["channel_title"],
            "thumbnail": video_info["thumbnail_url"],
            "viewCount": video_info["views"],
            "likeCount": video_info["likes"],
            "commentCount": video_info["comments"],
            "publishedAt": video_info["published_at"],
            "description": video_info["description"],
            "channelId": video_info["channel_id"]
        }
    except Exception as e:
        logger.error(f"비디오 정보 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_videos(request: SearchRequest):
    try:
        results = youtube_api.search_videos(request.query, request.max_results)
        return results
    except Exception as e:
        logger.error(f"비디오 검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate/{video_id}")
async def evaluate_video(video_id: str):
    try:
        # 비디오 정보 가져오기
        video_info = youtube_api.get_video_info(video_id)
        
        # 출처 신뢰도 평가
        source_trust = evaluator.evaluate_source_trust(video_info)
        
        # 내용 신뢰도 평가
        content_trust = evaluator.evaluate_content_trust(video_info)
        
        # 종합 점수 계산 (ScoreCalculator 사용)
        final_score = score_calculator.calculate_score(
            trust_score=source_trust["total_score"],
            content_score=content_trust["total_score"]
        )
        
        # 등급 및 설명 추가
        grade = score_calculator.get_grade(final_score)
        grade_description = score_calculator.get_grade_description(grade)
        
        return {
            "video_info": video_info,
            "source_trust": source_trust,
            "content_trust": content_trust,
            "final_score": final_score,
            "grade": grade,
            "grade_description": grade_description
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"비디오 평가 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="비디오 평가 중 오류가 발생했습니다.")

# 관리자 설정 관련 엔드포인트
@app.get("/api/admin/config")
async def get_admin_config(current_user: User = Depends(get_current_admin_user)):
    try:
        config = redis_client.get(ADMIN_CONFIG_KEY)
        return json.loads(config) if config else default_admin_config
    except Exception as e:
        logger.error(f"관리자 설정 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/config")
async def update_admin_config(config: AdminConfig, current_user: User = Depends(get_current_admin_user)):
    try:
        # 현재 설정 저장
        redis_client.set(ADMIN_CONFIG_KEY, json.dumps(config.dict()))
        
        # 변경 이력 저장
        history = {
            "timestamp": datetime.utcnow().isoformat(),
            "changes": json.dumps(config.dict()),
            "user": current_user.username
        }
        redis_client.rpush(CONFIG_HISTORY_KEY, json.dumps(history))
        
        return {"message": "설정이 업데이트되었습니다."}
    except Exception as e:
        logger.error(f"관리자 설정 업데이트 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/history")
async def get_config_history(current_user: User = Depends(get_current_admin_user)):
    try:
        history = redis_client.lrange(CONFIG_HISTORY_KEY, 0, -1)
        return [json.loads(item) for item in history]
    except Exception as e:
        logger.error(f"설정 변경 이력 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/config/pending")
async def submit_pending_changes(config: AdminConfig, current_user: User = Depends(get_current_admin_user)):
    try:
        change = {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "config": config.dict(),
            "user": current_user.username,
            "status": "pending"
        }
        redis_client.rpush(PENDING_CHANGES_KEY, json.dumps(change))
        return {"message": "변경 요청이 제출되었습니다.", "change_id": change["id"]}
    except Exception as e:
        logger.error(f"변경 요청 제출 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/config/pending")
async def get_pending_changes(current_user: User = Depends(get_current_admin_user)):
    try:
        changes = redis_client.lrange(PENDING_CHANGES_KEY, 0, -1)
        return [json.loads(change) for change in changes if json.loads(change)["status"] == "pending"]
    except Exception as e:
        logger.error(f"대기 중인 변경 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/config/approve")
async def approve_changes(change_id: str, current_user: User = Depends(get_current_admin_user)):
    try:
        # 대기 중인 변경 찾기
        changes = redis_client.lrange(PENDING_CHANGES_KEY, 0, -1)
        for i, change_str in enumerate(changes):
            change = json.loads(change_str)
            if change["id"] == change_id and change["status"] == "pending":
                # 변경 승인
                change["status"] = "approved"
                change["approved_by"] = current_user.username
                change["approved_at"] = datetime.utcnow().isoformat()
                
                # Redis 업데이트
                redis_client.lset(PENDING_CHANGES_KEY, i, json.dumps(change))
                redis_client.set(ADMIN_CONFIG_KEY, json.dumps(change["config"]))
                
                # 변경 이력 저장
                history = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "changes": json.dumps(change["config"]),
                    "user": current_user.username
                }
                redis_client.rpush(CONFIG_HISTORY_KEY, json.dumps(history))
                
                return {"message": "변경이 승인되었습니다."}
        
        raise HTTPException(status_code=404, detail="변경 요청을 찾을 수 없습니다.")
    except Exception as e:
        logger.error(f"변경 승인 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/config/rollback")
async def rollback_config(history_id: int, current_user: User = Depends(get_current_admin_user)):
    try:
        # 변경 이력 가져오기
        history = redis_client.lrange(CONFIG_HISTORY_KEY, history_id, history_id)
        if not history:
            raise HTTPException(status_code=404, detail="변경 이력을 찾을 수 없습니다.")
        
        # 설정 롤백
        config = json.loads(json.loads(history[0])["changes"])
        redis_client.set(ADMIN_CONFIG_KEY, json.dumps(config))
        
        # 롤백 이력 저장
        rollback = {
            "timestamp": datetime.utcnow().isoformat(),
            "changes": json.dumps(config),
            "user": current_user.username,
            "rollback_from": history_id
        }
        redis_client.rpush(CONFIG_HISTORY_KEY, json.dumps(rollback))
        
        return {"message": "설정이 롤백되었습니다."}
    except Exception as e:
        logger.error(f"설정 롤백 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_source_analysis(source_trust: Dict) -> str:
    """출처 신뢰도 분석 결과 생성"""
    try:
        score = source_trust["total_score"]
        if score >= 0.8:
            return "매우 신뢰할 수 있는 출처입니다."
        elif score >= 0.6:
            return "신뢰할 수 있는 출처입니다."
        elif score >= 0.4:
            return "보통 수준의 출처입니다."
        else:
            return "신뢰도가 낮은 출처입니다."
    except Exception as e:
        logger.error(f"출처 신뢰도 분석 결과 생성 중 오류 발생: {str(e)}")
        raise

def _generate_content_analysis(content_trust: Dict) -> str:
    """내용 신뢰도 분석 결과 생성"""
    try:
        score = content_trust["total_score"]
        if score >= 0.8:
            return "매우 신뢰할 수 있는 내용입니다."
        elif score >= 0.6:
            return "신뢰할 수 있는 내용입니다."
        elif score >= 0.4:
            return "보통 수준의 내용입니다."
        else:
            return "신뢰도가 낮은 내용입니다."
    except Exception as e:
        logger.error(f"내용 신뢰도 분석 결과 생성 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 