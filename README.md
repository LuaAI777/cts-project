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
│   ├── 📁 models/                   # Pydantic 모델
│   └── 📁 utils/                    # 유틸리티 함수
├── 📁 credentials/                  # 실제 .env 파일 위치
│   └── .env                         # 실제 환경변수
├── docker-compose.yml              # 전체 서비스 구성
└── README.md                       # 프로젝트 설명서
```

## 시작하기

### 사전 요구사항
- Docker
- Docker Compose

### 설치 및 실행
1. 저장소 클론
```bash
git clone [repository-url]
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

4. API 접속
- http://localhost:8000 에서 API 서버에 접근 가능
- http://localhost:8000/docs 에서 API 문서 확인 가능

## 개발 가이드
- 새로운 기능 추가 시 `backend/modules/` 디렉토리에 모듈 추가
- API 엔드포인트는 `main.py`에 등록
- 모델 정의는 `backend/models/` 디렉토리에 추가
- 유틸리티 함수는 `backend/utils/` 디렉토리에 추가

## 라이선스
[라이선스 정보] 