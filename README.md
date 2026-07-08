# PaceFlow

> 건설 현장의 자재 수급 지연을 줄이기 위한 대체 자재·공급사 추천 플랫폼

PaceFlow는 건설 현장에서 필요한 자재가 부족하거나 납품이 지연될 때, 대체 가능한 자재와 공급사를 빠르게 검토할 수 있도록 돕는 B2B 플랫폼입니다.

요청자가 필요한 자재와 현장 정보를 입력하면, 시스템은 자재 규격, 물성, 공급사 위치, 단가, 납품 이력 등을 종합적으로 비교해 추천 후보를 제공합니다. 단순히 공급사를 나열하는 것이 아니라, 추천 점수 기반으로 후보를 선별하고 지도에서 위치를 함께 확인할 수 있도록 구성했습니다.

---

## 프로젝트 개요

건설 현장에서는 특정 자재의 수급이 지연되면 공정 전체가 밀릴 수 있습니다. 하지만 대체 자재를 검토하고, 실제 납품 가능한 공급사를 찾고, 거리와 단가까지 비교하는 과정은 많은 시간이 필요합니다.

PaceFlow는 이 문제를 해결하기 위해 다음 흐름을 제공합니다.

1. 요청자가 필요한 자재와 현장 정보를 입력합니다.
2. 시스템이 대체 가능한 자재와 공급사 후보를 추천합니다.
3. 추천 후보의 점수, 위치, 단가, 납품 이력을 비교합니다.
4. 요청자는 적합한 공급사에게 문의를 보낼 수 있습니다.
5. 공급사는 문의를 확인하고 상태를 관리할 수 있습니다.

---

## 주요 사용자

| 역할  | 설명                               |
| --- | -------------------------------- |
| 요청자 | 필요한 자재를 등록하고 추천 공급사 후보를 확인하는 사용자 |
| 공급사 | 취급 자재를 등록하고 요청자의 문의를 확인하는 사용자    |

---

## 핵심 기능

### 1. 자재 요청

요청자는 현장명, 현장 위치, 필요 자재, 수량, 납기, 메모 등을 입력해 자재 수요를 등록할 수 있습니다.

등록된 요청 정보는 추천 후보를 계산할 때 입력값으로 활용됩니다.

### 2. 대체 자재·공급사 추천

PaceFlow는 자재 적합도, 공급 신뢰도, 거리/경로, 가격 정보를 종합해 공급사 후보를 추천합니다.

추천 결과는 점수 기반으로 정렬되며, 사용자는 추천 후보를 카드, 랭킹 테이블, 지도에서 확인할 수 있습니다.

### 3. 지도 기반 공급사 확인

추천 후보는 카카오맵 기반 지도에 표시됩니다.

기본적으로는 추천 점수 기준 `TOP 10` 공급사를 지도에 표시하며, 필요하면 `추천 후보 전체 보기`를 통해 현재 조건에 맞는 전체 추천 후보를 확인할 수 있습니다.

지도는 전체 공급사 DB를 그대로 표시하는 것이 아니라, 현재 자재 요청 조건을 통과한 추천 후보를 기준으로 표시합니다.

### 4. 공급사 문의

요청자는 추천 결과에서 공급사에게 직접 문의를 보낼 수 있습니다.

문의에는 자재명, 규격, 수량, 희망 납기, 현장 주소, 연락처, 메시지 등이 포함됩니다.

공급사는 문의 내역을 확인하고 상태를 관리할 수 있습니다.

### 5. 공급사 직접 등록

공급사 계정은 자신이 취급하는 자재, 규격, 가격, 재고 여부, 서비스 가능 지역 등을 직접 등록할 수 있습니다.

직접 등록된 공급사 데이터는 공공 계약 이력과 별도로 관리되며, 추천 화면에서 추가 후보로 함께 비교될 수 있습니다.

### 6. 커뮤니티

사용자는 대체 자재 후기, 공급사 후기, 현장 질문 등을 커뮤니티에 작성할 수 있습니다.

게시글, 댓글, 1:1 연락 요청 기능을 통해 운영 중 사용자 상호작용 데이터가 축적될 수 있는 구조를 갖추고 있습니다.

---

## 추천 시스템 구조

PaceFlow의 추천 시스템은 단순 거리 기반 추천이 아니라, 여러 요소를 종합한 점수 기반 추천 구조입니다.

### 추천 점수 구성

백엔드 추천 로직은 다음 요소를 기반으로 점수를 계산합니다.

| 요소     | 설명                        | 반영 방식                            |
| ------ | ------------------------- | -------------------------------- |
| 자재 적합도 | 요청 자재와 후보 자재의 규격·물성 적합 여부 | Hard Filter 통과 여부 기반             |
| 공급 신뢰도 | 해당 공급사의 납품 이력 수           | SupplyHistory 개수 기반              |
| 거리/경로  | 현장과 공급사 간 거리 및 차량 경로      | 카카오모빌리티 Directions API 기반        |
| 가격     | 후보 공급사의 단가                | 후보군 최저가 대비 상대 점수                 |
| 자재군 경험 | 정확 자재는 아니지만 같은 자재군 취급 경험  | CategoryContractHistory 기반 보조 점수 |

추천 점수는 자재 적합도, 공급 신뢰도, 거리/경로, 가격을 중심으로 계산하고, 자재군 경험은 보조 점수로만 반영합니다.

### 추천 결과 표시

프론트엔드에서는 여러 추천 후보 소스를 결합해 화면에 표시합니다.

* 백엔드 추천 API 결과
* 공급사 직접 등록 데이터
* 캐시된 계약 이력 기반 후보
* MVP/demo fallback 후보

화면에서는 빠른 의사결정을 위한 `TOP 5 카드`, 위치 확인을 위한 `추천 TOP 10 지도`, 전체 비교를 위한 `추천 후보 전체 랭킹`을 제공합니다.

---

## 데이터 확보 및 활용 구조

PaceFlow는 하나의 데이터 출처에만 의존하지 않고, 여러 경로의 데이터를 결합해 추천 후보를 구성합니다.

### 1. 요청자 입력 데이터

요청자가 입력한 현장 위치, 필요 자재, 수량, 납기 정보는 추천 API 호출 조건으로 사용됩니다.

관련 모델:

* Demand
* SupplierInquiry

### 2. 공급사 직접 등록 데이터

공급사가 직접 입력한 취급 자재, 규격, 가격, 재고 여부, 서비스 가능 지역 정보는 별도 후보 데이터로 관리됩니다.

관련 모델:

* SupplierMaterialRegistration

### 3. 내부 시드 및 초기 구축 데이터

초기 추천 기능을 검증하기 위해 KS 자재, 규격, 물성, 공급사, 납품 이력 데이터를 시드로 구축했습니다.

관련 데이터:

* Material
* MaterialSpec
* RegulationMapping
* Supplier
* SupplyHistory

### 4. 외부 데이터/API 기반 보강 데이터

공공 계약 이력 및 외부 API를 통해 공급사와 납품 이력 데이터를 보강합니다.

활용 예시:

* 공공 조달 계약 정보 기반 납품 이력 수집
* 조달청 종합쇼핑몰 후보 수집
* 도로명주소 API 기반 주소 검색
* 카카오 API 기반 좌표 변환 및 경로 계산

### 5. 운영 중 누적 데이터

서비스 이용 과정에서 문의, 커뮤니티 게시글, 댓글, 1:1 연락 요청 데이터가 누적됩니다.

현재 이 데이터는 추천 점수에 직접 반영되지는 않지만, 향후 공급사 응답률, 사용자 후기, 커뮤니티 신뢰도 등으로 확장할 수 있습니다.

---

## 데이터 정제 및 매핑 전략

PaceFlow는 외부 계약 데이터를 무조건 추천 데이터로 사용하지 않습니다.

수집된 계약 정보가 내부 자재 마스터와 정확히 매핑되는지 검토하고, 정확도가 부족한 데이터는 별도 보류 이력으로 분리합니다.

### SupplyHistory

`SupplyHistory`는 특정 자재로 정확히 매핑 가능한 계약 이력입니다.

이 데이터는 추천 점수 계산에 직접 사용됩니다.

활용 항목:

* 공급사의 납품 횟수
* 최신 단가
* 가격 점수
* 단가 추이
* 공급 신뢰도

### CategoryContractHistory

`CategoryContractHistory`는 자재군은 확인되지만 특정 KS 자재나 규격으로 확정하기 어려운 계약 이력입니다.

예를 들어 다음과 같은 경우는 정확 자재로 강제 매핑하지 않고 자재군 이력으로 분리합니다.

* 두께 미확정
* 등급 미확정
* 복수 KS 후보 발생
* 전선관 종류 미확정
* 전선관 규격 미확정
* 명시 규격과 일치하는 후보 없음

이 데이터는 가격, 단가 추이, 정확 자재 납품 횟수에는 직접 사용하지 않습니다. 대신 공급사의 자재군 취급 경험을 나타내는 보조 신뢰도 점수로만 활용합니다.

### 데이터 오염 방지

불확실한 계약을 정확 자재 이력으로 저장하면 추천 점수, 가격 비교, 단가 추이가 왜곡될 수 있습니다.

PaceFlow는 이를 막기 위해 다음과 같은 기준을 적용합니다.

* 정확 자재 매핑 가능 시 SupplyHistory 저장
* 자재군까지만 확인 가능하면 CategoryContractHistory 저장
* 복합 제품 의심 데이터 제외
* 지원하지 않는 자재군 제외
* 공급사 정보 없음, 계약일 없음, 유효 단가 없음 데이터 제외
* 중복 계약 데이터 저장 방지

이를 통해 데이터 양을 늘리면서도 추천 품질을 떨어뜨리는 오매핑을 방지했습니다.

---

## 주요 데이터 모델

| 모델                           | 역할                                |
| ---------------------------- | --------------------------------- |
| Material                     | KS 규격, 등급, 치수 등을 기준으로 관리되는 자재 마스터 |
| Supplier                     | 공급사 기본 정보, 주소, 좌표, 연락처 등을 관리      |
| SupplierMaterialRegistration | 공급사가 직접 등록한 취급 자재와 납품 가능 정보       |
| Demand                       | 요청자의 현장 위치, 필요 자재, 수량, 납기 정보를 저장  |
| SupplyHistory                | 특정 자재로 정확히 매핑된 공급사 계약·납품 이력       |
| CategoryContractHistory      | 정확 자재로 확정하기 어려운 자재군 단위 계약 이력      |
| SupplierInquiry              | 요청자와 공급사 간 자재 문의 및 상태 관리          |
| CommunityPost                | 대체 자재 후기, 공급사 후기, 현장 질문 게시글       |
| CommunityComment             | 커뮤니티 게시글 댓글                       |
| CommunityContactRequest      | 커뮤니티 게시글 작성자에게 보내는 1:1 연락 요청      |

---

## 기술 스택

### Frontend

* Vue 3
* Vite
* Vue Router
* Axios
* JavaScript ES Module
* Kakao Map JavaScript API

### Backend

* Django 5
* Django REST Framework
* DRF Token Authentication
* django-cors-headers
* python-dotenv
* requests

### Database

* SQLite
* PostgreSQL 지원 가능

`DATABASE_URL`이 설정되어 있으면 PostgreSQL을 사용하고, 없으면 로컬 SQLite DB를 사용합니다.

### External API / Data

* 도로명주소 API
* 카카오 주소 검색 API
* 카카오 키워드 검색 API
* 카카오모빌리티 Directions API
* 카카오 JavaScript 지도 API
* 공공 조달 계약 정보 API
* 조달청 종합쇼핑몰 API 수집 스크립트

---

## 프로젝트 구조

```text
1st-semester-pjt/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── apiClient.js
│   │   │   ├── authApi.js
│   │   │   ├── materialApi.js
│   │   │   ├── communityApi.js
│   │   │   └── notificationApi.js
│   │   ├── components/
│   │   │   ├── HeaderNav.vue
│   │   │   ├── KakaoMap.vue
│   │   │   ├── NotificationBell.vue
│   │   │   └── RecommendationCard.vue
│   │   ├── pages/
│   │   │   ├── HomePage.vue
│   │   │   ├── MaterialRequestPage.vue
│   │   │   ├── RecommendationPage.vue
│   │   │   ├── RecommendationDetailPage.vue
│   │   │   ├── SupplierProfilePage.vue
│   │   │   ├── SupplierMyPage.vue
│   │   │   ├── DashboardPage.vue
│   │   │   ├── InquiryDetailPage.vue
│   │   │   ├── CommunityPage.vue
│   │   │   ├── CommunityDetailPage.vue
│   │   │   └── CommunityWritePage.vue
│   │   └── router.js
│   └── package.json
│
├── back/
│   ├── accounts/
│   ├── config/
│   │   └── settings.py
│   ├── core/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── services/
│   │       └── kakao_directions.py
│   ├── scripts/
│   │   ├── seed_data.py
│   │   ├── seed_targeted_candidates.py
│   │   ├── collect_narajangteo.py
│   │   └── collect_shopping_mall.py
│   └── manage.py
└── README.md
```

---

## 실행 방법

### 1. Backend 실행

```bash
cd back
```

가상환경이 없다면 생성합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

마이그레이션을 실행합니다.

```bash
python manage.py migrate
```

개발 서버를 실행합니다.

```bash
python manage.py runserver
```

또는 프로젝트에서 사용하던 가상환경 경로를 그대로 사용할 경우:

```bash
.venv/bin/python3 manage.py runserver
```

### 2. Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

### 3. Frontend 빌드

```bash
cd frontend
npm run build
```

### 4. Backend 검증

```bash
cd back
.venv/bin/python3 manage.py check
```

### 5. 테스트 실행

```bash
cd back
.venv/bin/python3 manage.py test
```

---

## 환경변수

### Frontend

프론트엔드는 `frontend/.env.local` 파일을 사용합니다.

예시:

```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_KAKAO_JAVASCRIPT_KEY=your_kakao_javascript_key
VITE_GMS_KEY=your_key
```

### Backend

백엔드는 `back/.env` 파일을 사용합니다.

예시:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=

NARAJANGTEO_API_KEY=your_key
NARA_API_KEY=your_key
NARAJANGTEO_USER_API_KEY=your_key

JUSO_SEARCH_API_KEY=your_key
JUSO_API_KEY=your_key

KAKAO_REST_API_KEY=your_key
KAKAO_MAP_KEY=your_key

SHOPPING_MALL_API_KEY=your_key
```

> 실제 API 키와 `.env`, `.env.local` 파일은 Git에 올리지 않습니다.

---

## 데이터 수집 및 보강 스크립트

PaceFlow는 내부 시드 데이터와 외부 데이터 보강 스크립트를 함께 사용합니다.

### 초기 데이터 시드

```bash
cd back
.venv/bin/python3 scripts/seed_data.py
```

```bash
cd back
.venv/bin/python3 scripts/seed_targeted_candidates.py
```

### 공공 계약 이력 수집

```bash
cd back
.venv/bin/python3 scripts/collect_narajangteo.py --material 시멘트 --search 시멘트 --start-date 2025-12-01 --end-date 2025-12-07 --dry-run
```

`--dry-run` 옵션을 사용하면 DB 저장 없이 매핑 결과를 미리 확인할 수 있습니다.

실제 저장 전에는 반드시 dry-run으로 다음 항목을 확인하는 것을 권장합니다.

* 신규 후보 수
* 보류 사유
* 제외 사유
* 대표 샘플
* 보류 샘플

### 조달청 종합쇼핑몰 후보 수집

```bash
cd back
.venv/bin/python3 scripts/collect_shopping_mall.py
```

---

## 주요 API

| 기능           | Method | Endpoint                                        |
| ------------ | -----: | ----------------------------------------------- |
| 자재 요청 등록     |   POST | `/api/v1/demands/`                              |
| 대체 공급사 추천    |    GET | `/api/v1/materials/<material_id>/alternatives/` |
| 공급사 자재 등록    |   POST | `/api/v1/supplier-materials/`                   |
| 공급사 등록 자재 조회 |    GET | `/api/v1/supplier-materials/`                   |
| 공개 공급사 자재 조회 |    GET | `/api/v1/supplier-materials/public/`            |
| 공급사 문의 등록    |   POST | `/api/v1/inquiries/`                            |
| 차량 경로 조회     |   POST | `/api/v1/routes/driving/`                       |
| 외부 계약정보 조회   |    GET | `/api/v1/narajangteo/contracts/`                |
| 캐시 계약정보 조회   |    GET | `/api/v1/narajangteo/cached-contracts/`         |

---

## 주요 성과 및 개선 포인트

### 1. 추천 점수 기반 공급사 선별

단순히 가까운 공급사를 보여주는 것이 아니라, 자재 적합도, 납품 이력, 가격, 경로 정보를 종합해 추천 점수를 계산했습니다.

### 2. 정확 이력과 보류 이력 분리

정확한 자재로 매핑 가능한 계약은 `SupplyHistory`에 저장하고, 규격이 불명확한 계약은 `CategoryContractHistory`로 분리했습니다.

이를 통해 불확실한 데이터가 가격, 단가 추이, 납품 횟수에 섞이는 문제를 방지했습니다.

### 3. 데이터 오염 방지

수집 데이터 중 복합 제품, 지원하지 않는 자재군, 규격 미확정, 공급사 정보 없음, 유효 단가 없음 등은 추천에 직접 반영하지 않도록 필터링했습니다.

### 4. 지도 기반 추천 후보 표시

추천 후보는 카카오맵에서 위치와 함께 확인할 수 있습니다.

기본적으로 추천 TOP 10을 보여주고, 필요하면 추천 후보 전체를 지도에서 확인할 수 있도록 분리했습니다.

### 5. 역할 기반 서비스 흐름

요청자는 자재를 요청하고 공급사에게 문의할 수 있으며, 공급사는 취급 자재를 등록하고 문의를 관리할 수 있습니다.

### 6. 운영 데이터 누적 구조

문의, 커뮤니티 게시글, 댓글, 1:1 연락 요청 데이터가 별도 모델로 누적되도록 구성해 향후 신뢰도 평가나 추천 고도화에 활용할 수 있는 기반을 마련했습니다.

---

## Team

본 프로젝트는 2인 팀으로 진행했으며, 프론트엔드와 백엔드를 엄격히 분리하지 않고 기능 단위로 협업했습니다.

| 팀원    | 역할                                                 |
| ----- | -------------------------------------------------- |
| 황민정    | 서비스 기획, 추천 화면 UI/UX, 지도 기반 공급사 확인, 문의 흐름 구현        |
| 장우창 | 서비스 기획, 데이터 모델링, 계약 이력 정제, 추천 로직 및 데이터 오염 방지 구조 개선 |

---

## 향후 개선 방향

* 외부 데이터 수집 경로 확장
* 운영 데이터 기반 공급사 신뢰도 고도화
* 문의 응답률, 거래 성사 여부 등을 반영한 추천 점수 개선
* 지도 마커 클러스터링 및 필터 UX 개선
* CategoryContractHistory의 보류 데이터 검토/승인 관리 기능 추가
* 공급사 직접 등록 데이터와 공공 계약 이력 간 정합성 검증 강화
* 테스트 커버리지 확대 및 외부 API 실패 상황에 대한 상태값 정리

---

## 확인 필요 항목

README 최종 반영 전 아래 항목은 추가 확인이 필요합니다.

* 최종 프로젝트명을 `PaceFlow`로 통일할지 여부
* 기존 기획명 `Build-Safe Connector`를 부제로 남길지 여부
* `VITE_GMS_KEY`의 정확한 용도
* `KAKAO_MAP_KEY`가 백엔드에서 실제로 필요한지 여부
* 배포 환경에서 SQLite를 사용할지 PostgreSQL을 사용할지 여부
* 공공 데이터 수집 스크립트 예시를 README에 어느 수준까지 포함할지 여부
* 프론트 추천 후보에 포함되는 MVP/demo fallback 데이터를 README에서 어떻게 설명할지 여부
