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
load_dotenv(".env")

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

# 대기 중인 변경 사항
pending_changes = []

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
        raise HTTPException(status_code=500, detail=str(e))

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

def _generate_source_analysis(score: float) -> str:
    if score >= 0.8:
        return "출처가 매우 신뢰할 수 있습니다."
    elif score >= 0.6:
        return "출처가 대체로 신뢰할 수 있습니다."
    elif score >= 0.4:
        return "출처의 신뢰도가 보통입니다."
    else:
        return "출처의 신뢰도가 낮습니다."

def _generate_content_analysis(score: float) -> str:
    if score >= 0.8:
        return "내용이 매우 신뢰할 수 있습니다."
    elif score >= 0.6:
        return "내용이 대체로 신뢰할 수 있습니다."
    elif score >= 0.4:
        return "내용의 신뢰도가 보통입니다."
    else:
        return "내용의 신뢰도가 낮습니다."

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
@app.post("/api/admin/config/pending")
async def submit_pending_changes(change: dict):
    global pending_changes
    pending_changes.append(change)
    return {"message": "변경 요청이 제출되었습니다."}

@app.get("/api/admin/config/pending")
async def get_pending_changes(current_user: User = Depends(get_current_admin_user)):
    return pending_changes

@app.post("/api/admin/config/approve")
async def approve_changes(change_id: str, current_user: User = Depends(get_current_admin_user)):
    try:
        # 대기 중인 변경 사항에서 해당 ID의 변경 사항 찾기
        change_to_approve = None
        for change in pending_changes:
            if change.get("id") == change_id:
                change_to_approve = change
                break
        
        if not change_to_approve:
            raise HTTPException(status_code=404, detail="변경 사항을 찾을 수 없습니다.")
        
        # 설정 업데이트
        admin_config.update(change_to_approve["config"])
        
        # 변경 이력에 추가
        config_history.append({
            "timestamp": datetime.now(),
            "changes": json.dumps(change_to_approve["config"], ensure_ascii=False),
            "user": current_user.username
        })
        
        # 대기 중인 변경 사항에서 제거
        pending_changes = [change for change in pending_changes if change.get("id") != change_id]
        
        return {"message": "변경 사항이 승인되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# 설정 파일 경로
SETTING_FILE = "setting.json"
HISTORY_FILE = "setting_history.json"

# 기본 설정 구조
DEFAULT_SETTING = {
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

# 설정 파일 초기화
def init_setting_files():
    if not os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTING, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# 설정 파일 읽기
def read_setting():
    with open(SETTING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 설정 파일 쓰기
def write_setting(setting):
    with open(SETTING_FILE, 'w', encoding='utf-8') as f:
        json.dump(setting, f, ensure_ascii=False, indent=2)

# 이력 파일 읽기
def read_history():
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 이력 파일 쓰기
def write_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 이력 추가
def add_history_entry(change, user):
    history = read_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "changes": change
    })
    write_history(history)

# 설정 업데이트
def update_setting(new_setting, user):
    current_setting = read_setting()
    write_setting(new_setting)
    add_history_entry({
        "old": current_setting,
        "new": new_setting
    }, user)

# 모델 정의
class Setting(BaseModel):
    weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, Dict[str, int]]] = None
    keywords: Optional[Dict[str, List[str]]] = None

    class Config:
        extra = "allow"  # 추가 필드를 허용

class HistoryEntry(BaseModel):
    timestamp: str
    user: str
    changes: dict

# API 엔드포인트
@app.get("/api/admin/config")
async def get_config():
    return read_setting()

@app.post("/api/admin/config")
async def update_config(setting: Setting, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        update_setting(setting.dict(), username)
        return {"message": "설정이 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/admin/history")
async def get_history():
    return read_history()

@app.post("/api/admin/config/rollback")
async def rollback_config(entry: HistoryEntry, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        update_setting(entry.changes["old"], username)
        return {"message": "설정이 롤백되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 서버 시작 시 설정 파일 초기화
init_setting_files()

@app.get("/evaluate/{video_id}")
async def evaluate_video(video_id: str):
    try:
        # 비디오 정보 가져오기
        video_info = youtube_api.get_video_info(video_id)
        
        # 신뢰도 평가
        source_trust = evaluator.evaluate_source_trust(video_info)
        content_trust = evaluator.evaluate_content_trust(video_info)
        final_score = evaluator.calculate_final_score(source_trust, content_trust)
        
        return {
            "video_info": video_info,
            "trust_analysis": {
                "score": source_trust["total_score"],
                "details": _generate_source_analysis(source_trust["total_score"])
            },
            "content_analysis": {
                "score": content_trust["total_score"],
                "details": _generate_content_analysis(content_trust["total_score"])
            },
            "final_score": final_score["final_score"]
        }
    except Exception as e:
        print(f"Error in evaluate_video: {str(e)}")  # 디버깅을 위한 로그 추가
        raise HTTPException(status_code=500, detail=str(e))

def _generate_source_analysis(score: float) -> str:
    if score >= 0.8:
        return "출처가 매우 신뢰할 수 있습니다."
    elif score >= 0.6:
        return "출처가 대체로 신뢰할 수 있습니다."
    elif score >= 0.4:
        return "출처의 신뢰도가 보통입니다."
    else:
        return "출처의 신뢰도가 낮습니다."

def _generate_content_analysis(score: float) -> str:
    if score >= 0.8:
        return "내용이 매우 신뢰할 수 있습니다."
    elif score >= 0.6:
        return "내용이 대체로 신뢰할 수 있습니다."
    elif score >= 0.4:
        return "내용의 신뢰도가 보통입니다."
    else:
        return "내용의 신뢰도가 낮습니다."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 