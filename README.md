# CTS (Content Trust Score) 프로젝트

YouTube 콘텐츠의 신뢰도를 평가하는 웹 애플리케이션입니다. NLP 기술을 활용하여 콘텐츠의 출처와 내용을 분석하고 신뢰도 점수를 제공합니다.

## 주요 기능

- YouTube 콘텐츠 검색 및 분석
- 출처/채널 신뢰도 평가
  - 구독자 수 분석
  - 채널 활동 기간 평가
  - 시청자 참여도 분석
- 내용 신뢰도 평가
  - 제목 분석
  - 설명 분석
  - 감정 분석
- 평가 결과 히스토리 관리
- 모바일 반응형 UI

## 기술 스택

- Frontend: React, Vite
- Backend: FastAPI
- NLP: Hugging Face Transformers
- API: YouTube Data API

## 프로젝트 구조

```
cts-project/
├── frontend/                 # React 프론트엔드
│   ├── src/
│   │   ├── components/      # UI 컴포넌트
│   │   ├── contexts/        # React Context
│   │   ├── services/        # API 서비스
│   │   ├── constants/       # 상수 정의
│   │   ├── styles/          # CSS 스타일
│   │   └── pages/           # 페이지 컴포넌트
│   └── public/              # 정적 파일
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── core/           # 핵심 로직
│   │   ├── models/         # 데이터 모델
│   │   └── services/       # 비즈니스 로직
│   ├── modules/            # 기능 모듈
│   │   ├── evaluator.py    # 평가 로직
│   │   └── youtube.py      # YouTube API 통신
│   └── tests/              # 테스트 코드
└── README.md               # 프로젝트 문서
```

## 평가 기준

### 등급 기준
- A (0.8 이상): 매우 신뢰할 수 있음
- B (0.6 이상): 신뢰할 수 있음
- C (0.4 이상): 보통
- D (0.2 이상): 주의 필요
- F (0.2 미만): 신뢰할 수 없음

### 평가 요소
1. 출처/채널 신뢰도 (60%)
   - 구독자 수 (30%)
     - 100만 이상: 1.0
     - 10만 이상: 0.8
     - 1만 이상: 0.6
     - 1천 이상: 0.4
     - 그 외: 0.2
   - 활동 기간 (20%)
     - 5년 이상: 1.0
     - 3년 이상: 0.8
     - 1년 이상: 0.6
     - 그 외: 0.4
   - 참여도 (50%)
     - 좋아요/조회수 ≥ 0.1, 댓글/조회수 ≥ 0.01: 1.0
     - 좋아요/조회수 ≥ 0.05, 댓글/조회수 ≥ 0.005: 0.8
     - 좋아요/조회수 ≥ 0.02, 댓글/조회수 ≥ 0.002: 0.6
     - 그 외: 0.4

2. 내용 신뢰도 (40%)
   - 제목 분석 (30%)
     - 길이 10-100자: 1.0
     - 길이 5-150자: 0.8
     - 그 외: 0.6
   - 설명 분석 (40%)
     - 길이 100-5000자: 1.0
     - 길이 50-10000자: 0.8
     - 그 외: 0.6
   - 감정 분석 (30%)
     - 중립성 평가
     - 극단성 평가

## API 엔드포인트

### 비디오 평가
```http
POST /api/evaluate
Content-Type: application/json

{
  "video_id": "비디오ID"
}
```

응답:
```json
{
  "video_info": {
    "title": "비디오 제목",
    "channel": "채널명",
    "views": 1000000,
    "likes": 50000,
    "comments": 2000,
    "published_at": "2024-03-20T10:00:00Z"
  },
  "evaluation": {
    "source_trust": {
      "score": 0.85,
      "details": {
        "subscriber_score": 0.9,
        "activity_score": 0.8,
        "engagement_score": 0.85
      }
    },
    "content_trust": {
      "score": 0.75,
      "details": {
        "title_score": 0.8,
        "description_score": 0.7,
        "sentiment_score": 0.75
      }
    },
    "final_score": 0.81,
    "grade": "A"
  },
  "analysis": {
    "source_analysis": "채널의 구독자 수가 많고, 활동 기간이 길며, 시청자 참여도가 높습니다.",
    "content_analysis": "제목과 설명이 적절하며, 내용이 중립적이고 균형 잡혀 있습니다."
  }
}
```

### 비디오 검색
```http
POST /api/search
Content-Type: application/json

{
  "query": "검색어",
  "max_results": 10
}
```

## 설치 및 실행

### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

### 백엔드
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수를 설정합니다:

```
YOUTUBE_API_KEY=your_api_key
```

## 개발 가이드라인

1. **코드 스타일**
   - ESLint와 Prettier를 사용한 코드 포맷팅
   - 컴포넌트는 함수형으로 작성
   - CSS는 CSS Modules 또는 Styled Components 사용

2. **테스트**
   - Jest와 React Testing Library를 사용한 단위 테스트
   - Cypress를 사용한 E2E 테스트

3. **성능 최적화**
   - React.memo와 useMemo를 활용한 렌더링 최적화
   - 이미지 최적화 및 지연 로딩
   - 코드 스플리팅 적용

## 라이선스

MIT License
