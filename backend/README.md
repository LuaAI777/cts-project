# CTS 백엔드

## 기능

- YouTube API 연동
- 비디오 정보 수집 및 분석
- 신뢰도 평가 시스템
- 관리자 설정 관리 API
  - 설정 저장 및 조회
  - 변경 이력 관리
  - 변경 승인 프로세스
  - 설정 롤백 기능

## 기술 스택

- FastAPI
- Python 3.12
- Redis
- JWT 인증

## 시작하기

### 필수 조건

- Python 3.12 이상
- Redis 서버
- YouTube API 키

### 설치

```bash
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일 생성:
```env
YOUTUBE_API_KEY=your_api_key
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=your_secret_key
```

### 개발 서버 실행

```bash
uvicorn main:app --reload
```

## API 엔드포인트

### 비디오 평가
- `POST /api/evaluate`: 비디오 ID로 평가 수행
- `GET /youtube/video/{video_id}`: 비디오 정보 조회
- `POST /api/search`: 비디오 검색

### 관리자 API
- `GET /api/admin/config`: 현재 설정 조회
- `POST /api/admin/config`: 설정 업데이트
- `GET /api/admin/history`: 설정 변경 이력 조회
- `POST /api/admin/config/pending`: 변경 요청 제출
- `POST /api/admin/config/approve/{id}`: 변경 승인
- `POST /api/admin/config/rollback/{id}`: 설정 롤백

### 인증
- `POST /token`: JWT 토큰 발급

## 설정 관리

### 기본 설정 구조
```json
{
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
```

### 변경 관리 프로세스
1. 관리자가 변경 요청 제출
2. 변경 내용 검토
3. 승인 또는 거절
4. 승인된 변경 적용
5. 변경 이력 기록

## 보안

- JWT 토큰 기반 인증
- 관리자 권한 검증
- API 키 보호
- CORS 설정 