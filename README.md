# CTS (Content Trust Score) 프로젝트

## 프로젝트 개요
CTS는 유튜브 콘텐츠의 신뢰도를 평가하는 시스템입니다. NLP 기술을 활용하여 콘텐츠의 신뢰도를 분석하고 점수를 부여합니다.

## 프로젝트 구조
```
📁 cts-project/
├── 📁 backend/                       # FastAPI 앱 소스 코드
│   ├── main.py                      # 진입점
│   ├── requirements.txt            # 의존성 목록
│   ├── Dockerfile                  # FastAPI용 Docker 빌드 정의
│   ├── .env.example                # 공유용 환경변수 템플릿
│   ├── 📁 modules/                  # 기능 모듈
│   │   ├── youtube.py              # YouTube API 통신
│   │   ├── evaluator.py            # 총괄 평가 관리
│   │   ├── trust.py                # 출처 및 채널 분석
│   │   ├── nlp.py                  # 내용 분석
│   │   └── scoring.py              # 점수 계산 및 등급화
│   ├── 📁 models/                   # Pydantic 모델
│   └── 📁 utils/                    # 유틸리티 함수
├── 📁 frontend/                     # React 앱 소스 코드
│   ├── package.json                # npm 의존성
│   ├── vite.config.js              # Vite 설정
│   ├── Dockerfile                  # React 앱용 Docker 빌드 정의
│   ├── 📁 src/                     # 소스 코드
│   │   ├── 📁 components/          # 재사용 가능한 컴포넌트
│   │   │   ├── SearchBar.jsx      # 검색 입력 컴포넌트
│   │   │   ├── VideoCard.jsx      # 비디오 정보 카드
│   │   │   ├── ScoreCard.jsx      # 평가 결과 카드
│   │   │   └── LoadingSpinner.jsx # 로딩 인디케이터
│   │   ├── 📁 pages/              # 페이지 컴포넌트
│   │   │   ├── Home.jsx          # 메인 페이지
│   │   │   └── Result.jsx        # 결과 페이지
│   │   ├── 📁 styles/            # 스타일 파일
│   │   ├── 📁 utils/             # 유틸리티 함수
│   │   └── App.jsx               # 앱 진입점
├── 📁 credentials/                 # 실제 .env 파일 위치
│   └── .env                        # 실제 환경변수
├── docker-compose.yml             # 전체 서비스 구성
└── README.md                      # 프로젝트 설명서
```

## 시작하기

### 사전 요구사항
- Docker
- Docker Compose
- Node.js (개발용)

### 설치 및 실행
1. 저장소 클론
```bash
git clone https://github.com/LuaAI777/cts-project.git
cd cts-project
```

2. 환경 변수 설정
```bash
cp backend/.env.example credentials/.env
# credentials/.env 파일을 편집하여 필요한 API 키 등을 설정
```

3. 서비스 실행
```bash
docker-compose up --build
```

4. 접속
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 프론트엔드 UI

### 홈 페이지
- YouTube URL 또는 비디오 ID 입력
- 입력 유효성 검사
- 에러 메시지 표시

### 결과 페이지
- 비디오 정보 카드
  - 제목, 설명, 채널명
  - 조회수, 좋아요 수, 댓글 수
  - 게시일
- 신뢰도 평가 결과 카드
  - 종합 등급 (A~F)
  - 종합 점수
  - 출처/채널 신뢰도
  - 내용 신뢰도
- 로딩 상태 표시
- 에러 처리

## API 엔드포인트

### 환경 변수 확인
- GET `/env-check`
- 현재 설정된 환경 변수 확인

### YouTube API
- GET `/youtube/video/{video_id}`
  - 비디오 정보 조회
  - 예시: `http://localhost:8000/youtube/video/dQw4w9WgXcQ`

- GET `/youtube/search`
  - 비디오 검색
  - 파라미터:
    - `query`: 검색어
    - `max_results`: 최대 결과 수 (기본값: 10)
  - 예시: `http://localhost:8000/youtube/search?query=python&max_results=5`

### 콘텐츠 평가
- GET `/evaluate/{video_id}`
  - 비디오의 신뢰도를 종합적으로 평가
  - 평가 요소:
    - 출처/채널 신뢰도 (60%)
    - 내용 신뢰도 (40%)
  - 등급:
    - A: 0.8 이상 (매우 신뢰할 수 있음)
    - B: 0.6 이상 (신뢰할 수 있음)
    - C: 0.4 이상 (보통)
    - D: 0.2 이상 (주의 필요)
    - F: 0.2 미만 (신뢰할 수 없음)
  - 예시: `http://localhost:8000/evaluate/dQw4w9WgXcQ`

## 평가 요소 상세

### 출처/채널 분석 (TrustAnalyzer)
- 채널 신뢰도
  - 구독자 수
  - 채널 활동 기간
  - 과거 콘텐츠 평가
- 참여도 분석
  - 좋아요 비율
  - 댓글 비율
  - 조회수 대비 상호작용

### 내용 분석 (ContentAnalyzer)
- 제목 분석
  - 길이
  - 키워드
  - 감정 분석
- 설명 분석
  - 길이
  - 키워드
  - 링크 포함 여부
  - 감정 분석

### 점수 계산 (ScoreCalculator)
- 가중치 적용
  - 출처/채널: 60%
  - 내용: 40%
- 등급화
  - A~F 등급
  - 등급별 설명 제공

## 개발 가이드
- 새로운 기능 추가 시 `backend/modules/` 디렉토리에 모듈 추가
- API 엔드포인트는 `main.py`에 등록
- 모델 정의는 `backend/models/` 디렉토리에 추가
- 유틸리티 함수는 `backend/utils/` 디렉토리에 추가
- 프론트엔드 컴포넌트는 `frontend/src/components/` 디렉토리에 추가
- 프론트엔드 페이지는 `frontend/src/pages/` 디렉토리에 추가

## 라이선스
[라이선스 정보]
