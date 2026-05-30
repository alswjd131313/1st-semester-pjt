# PaceFlow Frontend V2

기존 `frontend` 폴더를 보존하고, 기능별로 다시 구현하기 위한 Vue 3 MVP 작업 공간입니다.

## 실행 방법

```bash
cd frontend
npm install
npm run dev
```

Vite가 터미널에 표시하는 `Local:` 주소로 접속합니다.

## API 전환 설정

기본값은 mock/localStorage 모드입니다. Django API가 준비되기 전까지는 별도 설정 없이 실행할 수 있습니다.

```bash
cp .env.example .env
```

```env
VITE_USE_MOCK=true
VITE_API_BASE_URL=http://localhost:8000
```

백엔드 API와 연결할 때는 아래처럼 변경합니다.

```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000
```

현재 연결 준비된 endpoint:

- `POST /api/requests/`
- `GET /api/recommendations/{requestId}/`
- `GET /api/supplier-materials/`
- `POST /api/supplier-materials/`
- `GET /api/inquiries/` MVP 프론트 확장용
- `POST /api/inquiries/` MVP 프론트 확장용
- `GET /api/inquiries/{inquiryId}/` MVP 프론트 확장용
- `PATCH /api/inquiries/{inquiryId}/` MVP 프론트 확장용

## 현재 1단계 범위

- Vue 3 + Vue Router + Axios 의존성 구성
- 공통 헤더와 기본 라우터 구성
- 메인 검색 화면 구현
- 검색어를 `/request` 페이지로 넘기는 최소 흐름 구현

## 현재 2단계 범위

- mock 로그인 구현
- 자재 요청자와 공급사 역할 분리
- `/request`는 자재 요청자만 접근
- `/supplier-register`는 공급사만 접근
- 로그인 상태를 `localStorage`에 저장

## 현재 3단계 범위

- 자재 요청 폼 입력
- 요청 제출 시 mock request 생성
- `/recommendations` 추천 결과 화면 이동
- 요청 요약과 더미 추천 공급사 카드 표시

## 현재 4단계 범위

- 공급사 취급 자재 등록
- 등록된 공급사 자재 목록 표시
- 등록된 공급사 자재를 추천 결과 후보에 반영

## 현재 5단계 범위

- 추천 카드 상세 보기 모달
- 공급 조건, 점수 분석, 추천 이유 표시
- 감리 승인 필요 여부 상세 안내

## 다음 구현 순서

1. 자재 요청 폼 완성
2. 요청 저장 mock API 연결
3. 추천 결과 카드 구현
4. 공급사 등록 화면 구현
5. Django API 연동으로 교체
