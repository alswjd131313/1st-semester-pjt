<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-motion-bg" aria-hidden="true">
        <span class="flow-line line-one"></span>
        <span class="flow-line line-two"></span>
        <span class="flow-line line-three"></span>
        <span class="data-node node-one"></span>
        <span class="data-node node-two"></span>
        <span class="data-node node-three"></span>
      </div>

      <div v-if="!authState.user" class="hero-copy">
        <p class="eyebrow">PaceFlow MVP</p>
        <h1>공사 지연은 막고,<br />대체 자재는 빠르게 찾으세요</h1>
        <p class="hero-description">
          규격, 물성 정보, 가격, 거리, 과거 납품 이력을 비교해 먼저 문의할 만한
          공급사 후보를 추천합니다.
        </p>

        <form class="search-box" @submit.prevent="goToRequest">
          <input
            v-model="keyword"
            type="search"
            placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종"
          />
          <button type="submit">대체 자재 찾기</button>
        </form>

        <div class="hero-actions">
          <RouterLink to="/login?role=requester">요청자 로그인</RouterLink>
          <RouterLink to="/login?role=supplier">공급사 로그인</RouterLink>
          <RouterLink to="/recommendations">추천 결과 보기</RouterLink>
        </div>
      </div>

      <div v-else-if="isRequester" class="hero-copy">
        <p class="eyebrow">Requester Workspace</p>
        <h1>{{ authState.user.name }}님,<br />필요 자재를 바로 요청하세요</h1>
        <p class="hero-description">
          현장 주소와 기준 자재를 등록하면 가격, 거리, 납품 이력을 비교한 공급사 후보를
          빠르게 확인할 수 있습니다.
        </p>

        <form class="search-box" @submit.prevent="goToRequest">
          <input
            v-model="keyword"
            type="search"
            placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종"
          />
          <button type="submit">자재 요청 시작</button>
        </form>

        <div class="hero-actions">
          <RouterLink to="/request">새 자재 요청</RouterLink>
          <RouterLink to="/dashboard">내 문의 내역</RouterLink>
          <RouterLink to="/recommendations">추천 결과 보기</RouterLink>
        </div>
      </div>

      <div v-else class="hero-copy">
        <p class="eyebrow">Supplier Workspace</p>
        <h1>{{ authState.user.name }}님,<br />등록 자재와 문의를 관리하세요</h1>
        <p class="hero-description">
          취급 자재를 등록하고 요청자가 남긴 문의 상태를 확인하세요. 견적 가능 여부를
          빠르게 표시하면 문의 우선순위가 더 명확해집니다.
        </p>

        <div class="supplier-action-panel">
          <RouterLink class="supplier-primary-action" to="/supplier-register">
            취급 자재 등록하기
          </RouterLink>
          <RouterLink to="/dashboard">접수 문의 확인</RouterLink>
          <RouterLink to="/recommendations">추천 노출 확인</RouterLink>
        </div>
      </div>

      <aside v-if="!authState.user" class="hero-panel">
        <span>연동 상태</span>
        <strong>백엔드 API 연결 완료</strong>
        <p>자재 검색, 수요 등록, 추천 결과는 Django API와 연결되어 있습니다. 지도와 주소 검증은 API 키 발급 후 연결합니다.</p>
        <div class="flow-list">
          <RouterLink to="/request">자재 요청 등록</RouterLink>
          <RouterLink to="/supplier-register">공급사 자재 등록</RouterLink>
          <RouterLink to="/recommendations">추천 상세 보기</RouterLink>
          <RouterLink to="/dashboard">문의 내역 확인</RouterLink>
        </div>
      </aside>

      <aside v-else class="hero-panel role-panel">
        <span>{{ roleLabel }} 요약</span>
        <strong>{{ roleHeadline }}</strong>
        <p>{{ roleDescription }}</p>
        <p v-if="isLoading" class="loading-message">요약 데이터를 불러오는 중입니다.</p>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <div class="role-stat-grid">
          <article v-for="item in roleStats" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </article>
        </div>

        <div class="flow-list">
          <RouterLink
            v-for="item in roleLinks"
            :key="item.to"
            :to="item.to"
          >
            {{ item.label }}
          </RouterLink>
        </div>
      </aside>
    </section>

    <section class="home-section trust-section">
      <div class="section-heading">
        <p class="eyebrow">Data Transparency</p>
        <h2>추천 결과의 출처를 먼저 보여줍니다</h2>
        <p>
          PaceFlow는 실시간 재고를 보장하지 않습니다. 현재 MVP에서는 백엔드 검증 데이터와
          추후 나라장터 계약 이력을 분리해 표시하도록 설계합니다.
        </p>
      </div>

      <div class="trust-grid">
        <article v-for="item in trustCards" :key="item.title" class="trust-card">
          <span>{{ item.label }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="home-section location-section">
      <div class="location-copy">
        <p class="eyebrow">Location Ready</p>
        <h2>지도 API 없이도 위치 흐름은 먼저 잡아둡니다</h2>
        <p>
          도로명주소 API가 연결되면 현장 주소를 표준화하고, 카카오맵 API가 연결되면
          현장과 공급사 위치를 같은 화면에서 비교합니다.
        </p>
        <div class="status-list">
          <span>현재: 성수동 기준 좌표로 거리 계산 검증</span>
          <span>예정: 도로명주소 검색과 좌표 변환</span>
          <span>예정: 카카오맵 공급사 핀 표시</span>
        </div>
      </div>

      <div class="map-preview" aria-label="지도 API 연결 예정 미리보기">
        <div class="map-grid" aria-hidden="true"></div>
        <span class="map-pin site-pin">현장</span>
        <span class="map-pin supplier-pin pin-a">성수철강</span>
        <span class="map-pin supplier-pin pin-b">한강스틸</span>
        <span class="map-pin supplier-pin pin-c">동부자재</span>
        <strong>지도 API 연결 예정</strong>
      </div>
    </section>

    <section class="home-section process-section">
      <div class="section-heading">
        <p class="eyebrow">MVP Flow</p>
        <h2>지금 검증 가능한 흐름</h2>
      </div>

      <div class="process-grid">
        <article v-for="step in processSteps" :key="step.title">
          <span>{{ step.step }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { authState } from "../api/authApi";
import { getSupplierInquiries, getSupplierMaterials } from "../api/materialApi";

const router = useRouter();
const keyword = ref("");
const inquiries = ref([]);
const supplierMaterials = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const trustCards = [
  {
    label: "데모 데이터",
    title: "로컬 seed 공급사",
    description: "성수철강, 한강스틸, 동부자재는 추천 API 검증을 위한 예시 데이터입니다.",
  },
  {
    label: "공공데이터 예정",
    title: "나라장터 계약 이력",
    description: "업체명, 사업자번호, 계약일, 계약 금액을 수집해 납품 이력 근거로 활용합니다.",
  },
  {
    label: "API 연결 예정",
    title: "주소와 지도 검증",
    description: "도로명주소와 카카오맵 API 키가 준비되면 주소 표준화와 위치 시각화를 연결합니다.",
  },
];
const processSteps = [
  {
    step: "01",
    title: "기준 자재 요청",
    description: "현장 담당자가 자재명, KS 규격, 강도 등급, 필요 날짜를 등록합니다.",
  },
  {
    step: "02",
    title: "백엔드 추천 계산",
    description: "Django API가 물성 조건, 가격, 거리, 납품 이력을 기준으로 후보를 정렬합니다.",
  },
  {
    step: "03",
    title: "문의 우선순위 확인",
    description: "추천 카드와 상세 보기에서 점수 근거와 승인 리스크를 확인합니다.",
  },
];
const isSupplier = computed(() => authState.user?.role === "supplier");
const isRequester = computed(() => authState.user?.role === "requester");
const roleLabel = computed(() => (isSupplier.value ? "공급사" : "요청자"));
const quotedCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.status === "quoted").length,
);
const approvalCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.supplier?.approvalRequired).length,
);
const roleHeadline = computed(() =>
  isSupplier.value ? "문의와 등록 자재를 한눈에" : "요청과 문의 상태를 한눈에",
);
const roleDescription = computed(() =>
  isSupplier.value
    ? "등록된 자재와 접수 문의를 확인하고, 공급 가능 여부를 빠르게 업데이트하세요."
    : "새 요청을 등록하고 추천 후보에 남긴 문의 상태를 이어서 확인하세요.",
);
const roleStats = computed(() => {
  if (isSupplier.value) {
    return [
      { label: "등록 자재", value: `${supplierMaterials.value.length}개` },
      { label: "접수 문의", value: `${inquiries.value.length}건` },
      { label: "견적 가능", value: `${quotedCount.value}건` },
    ];
  }

  return [
    { label: "저장 문의", value: `${inquiries.value.length}건` },
    { label: "견적 가능", value: `${quotedCount.value}건` },
    { label: "승인 확인", value: `${approvalCount.value}건` },
  ];
});
const roleLinks = computed(() => {
  if (isSupplier.value) {
    return [
      { label: "공급사 자재 등록", to: "/supplier-register" },
      { label: "문의 상태 관리", to: "/dashboard" },
      { label: "추천 노출 확인", to: "/recommendations" },
    ];
  }

  return [
    { label: "새 자재 요청", to: "/request" },
    { label: "내 문의 내역", to: "/dashboard" },
    { label: "추천 결과 확인", to: "/recommendations" },
  ];
});

onMounted(loadRoleSummary);

async function loadRoleSummary() {
  if (!authState.user) {
    return;
  }

  try {
    isLoading.value = true;
    errorMessage.value = "";
    inquiries.value = await getSupplierInquiries();
    supplierMaterials.value = await getSupplierMaterials();
  } catch {
    errorMessage.value = "역할별 요약 정보를 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function goToRequest() {
  router.push({
    path: "/request",
    query: keyword.value ? { keyword: keyword.value } : {},
  });
}
</script>
