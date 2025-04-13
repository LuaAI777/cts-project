# CTS 프론트엔드

## 기능

- YouTube 비디오 검색 및 평가
- 평가 결과 상세 분석
- 관리자 설정 관리
  - 평가 기준 가중치 조정
  - 구독자 수 기준 설정
  - 키워드 관리
  - 설정 변경 이력 관리
  - 변경 요청 및 승인 프로세스
  - 설정 롤백 기능

## 기술 스택

- React
- Vite
- Tailwind CSS
- Axios

## 시작하기

### 필수 조건

- Node.js 20 이상
- npm 또는 yarn

### 설치

```bash
npm install
# 또는
yarn install
```

### 개발 서버 실행

```bash
npm run dev
# 또는
yarn dev
```

### 빌드

```bash
npm run build
# 또는
yarn build
```

## 관리자 기능

### 로그인
- `/login` 경로에서 관리자 로그인 가능
- JWT 토큰 기반 인증

### 설정 관리
- 가중치 설정
  - 출처/채널 가중치
  - 내용 가중치
- 구독자 기준 설정
  - 높음/중간/낮음 기준값
- 키워드 관리
  - 신뢰성 키워드
  - 의심스러운 키워드

### 변경 관리
- 변경 요청 제출
- 대기 중인 변경 승인
- 설정 변경 이력 조회
- 이전 설정으로 롤백

## API 연동

- 백엔드 API 엔드포인트
  - `/api/admin/config`: 설정 조회/수정
  - `/api/admin/history`: 변경 이력 조회
  - `/api/admin/pending`: 대기 중인 변경 조회
  - `/api/admin/config/pending`: 변경 요청 제출
  - `/api/admin/config/approve/{id}`: 변경 승인
  - `/api/admin/config/rollback/{id}`: 설정 롤백

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript and enable type-aware lint rules. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
