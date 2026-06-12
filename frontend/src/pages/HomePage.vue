<template>
  <div class="home-page">
    <section class="hero-section pace-hero section-observe">
      <div class="hero-motion-bg motion-bg" aria-hidden="true">
        <span class="flow-line line-one"></span>
        <span class="flow-line line-two"></span>
        <span class="flow-line line-three"></span>
        <span class="data-node node node-one"></span>
        <span class="data-node node node-two"></span>
        <span class="data-node node node-three"></span>
      </div>

      <div class="pace-hero-copy">
        <p class="eyebrow">PaceFlow Material Intelligence</p>
        <h1>
          <span>공급이 막혀도,</span>
          <span>공사는 멈추지 않도록</span>
        </h1>
        <p class="hero-description">
          규격, 물성, 거리, 단가, 납품 이력을 한 번에 비교해 현장에서 먼저 문의할
          공급사 후보를 정리합니다.
        </p>
        <div class="hero-proof-row" aria-label="추천 기준">
          <span>물성 기준 검토</span>
          <span>거리·단가 비교</span>
          <span>납품 이력 반영</span>
        </div>
      </div>

      <aside class="pace-hero-panel">
        <template v-if="!authState.user">
          <span class="panel-label">Start PaceFlow</span>
          <h2>필요한 역할로 바로 시작하세요.</h2>
          <p>
            요청자는 대체 자재를 찾고, 공급사는 취급 자재와 문의 가능 상태를 관리합니다.
          </p>
          <div class="panel-action-stack">
            <RouterLink class="primary-button" to="/login?role=requester">
              요청자로 시작
            </RouterLink>
            <RouterLink class="secondary-button" to="/login?role=supplier">
              공급사로 시작
            </RouterLink>
          </div>
        </template>

        <template v-else>
          <span class="panel-label">{{ roleLabel }} Workspace</span>
          <h2>{{ roleHeadline }}</h2>
          <p>{{ roleDescription }}</p>
          <p v-if="isLoading" class="loading-message">요약 정보를 불러오는 중입니다.</p>
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

          <div class="compact-stat-row">
            <article v-for="item in roleStats" :key="item.label">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </article>
          </div>

          <div class="panel-action-stack compact">
            <RouterLink class="primary-button" :to="primaryRoleAction.to">
              {{ primaryRoleAction.label }}
            </RouterLink>
            <RouterLink class="secondary-button" :to="secondaryRoleAction.to">
              {{ secondaryRoleAction.label }}
            </RouterLink>
          </div>
        </template>
      </aside>

      <form class="hero-search-dock" @submit.prevent="submitSearch">
        <label>
          <span>자재 검색</span>
          <input
            v-model="keyword"
            type="search"
            placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종"
          />
        </label>
        <button type="submit">{{ searchButtonLabel }}</button>
        <RouterLink class="dock-link" :to="dockLink.to">{{ dockLink.label }}</RouterLink>
      </form>
    </section>

    <section class="value-strip section-observe">
      <div class="section-heading center-heading">
        <h2>현장 담당자의 시간을 아껴주는 <span>핵심 가치</span></h2>
      </div>

      <div class="value-grid">
        <article v-for="item in valueCards" :key="item.title">
          <span class="value-icon">{{ item.icon }}</span>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
        </article>
      </div>
    </section>

    <section class="flow-section section-observe">
      <div class="section-heading center-heading">
        <h2>자재 수급, 이렇게 간단합니다</h2>
      </div>

      <div class="flow-card-grid">
        <article v-for="item in workflowCards" :key="item.title">
          <span class="flow-step">{{ item.step }}</span>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
          <div :class="['flow-visual', item.visualType]" aria-hidden="true">
            <span></span>
            <i></i>
            <b></b>
          </div>
        </article>
      </div>
    </section>

    <section class="material-proof-section section-observe">
      <div class="section-heading center-heading">
        <h2>예시로 보는 <span>물성 비교</span></h2>
      </div>

      <div class="material-proof-card">
        <article class="material-mini-card">
          <span>원본 자재</span>
          <h3>{{ materialProof.original.name }}</h3>
          <div :class="['material-visual', materialProof.original.visualClass]" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <dl>
            <div>
              <dt>제조사</dt>
              <dd>{{ materialProof.original.maker }}</dd>
            </div>
            <div>
              <dt>등록일</dt>
              <dd>{{ materialProof.original.registeredAt }}</dd>
            </div>
          </dl>
        </article>

        <div class="property-compare-table">
          <div class="compare-row compare-head">
            <span>항목</span>
            <span>원본 자재</span>
            <span>추천 자재</span>
            <span>비교 결과</span>
          </div>
          <div v-for="row in materialComparisonRows" :key="row.label" class="compare-row">
            <span>{{ row.label }}</span>
            <span>{{ row.original }}</span>
            <span>{{ row.candidate }}</span>
            <strong>{{ row.result }}</strong>
          </div>
          <p class="comparison-result">물성 동등성 검증 완료</p>
        </div>

        <article class="material-mini-card recommended">
          <span>추천 자재</span>
          <h3>{{ materialProof.candidate.name }}</h3>
          <div :class="['material-visual', materialProof.candidate.visualClass]" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <dl>
            <div>
              <dt>제조사</dt>
              <dd>{{ materialProof.candidate.maker }}</dd>
            </div>
            <div>
              <dt>등록일</dt>
              <dd>{{ materialProof.candidate.registeredAt }}</dd>
            </div>
          </dl>
        </article>
      </div>
    </section>

    <section class="recommend-reason-section section-observe">
      <div class="section-heading center-heading">
        <h2>왜 이 공급사를 추천할까요?</h2>
      </div>

      <div class="reason-grid">
        <article v-for="item in reasonCards" :key="item.title">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="service-scope-section section-observe">
      <div class="scope-illustration" aria-hidden="true">
        <div class="scope-preview-card main-preview"></div>
        <div class="scope-preview-card side-preview"></div>
        <span class="scope-search-ring"></span>
      </div>
      <div class="scope-copy">
        <p class="eyebrow">Service Scope</p>
        <h2>실시간 거래 플랫폼이 아닙니다.</h2>
        <p>
          PaceFlow는 구매를 대신하지 않습니다. 대신 현장 담당자가 여러 공급사를 탐색하고
          비교하는 과정을 몇 분 안에 끝낼 수 있도록 돕는 의사결정 지원 플랫폼입니다.
        </p>
        <ul>
          <li v-for="item in scopeItems" :key="item">{{ item }}</li>
        </ul>
      </div>
    </section>

    <section class="bottom-cta-section section-observe">
      <div>
        <h2>지금 바로 대체 자재를 검색하고, 최적의 공급사 후보를 확인해보세요.</h2>
      </div>
      <div>
        <RouterLink class="primary-button" to="/request">대체 자재 찾기</RouterLink>
        <RouterLink class="secondary-button" to="/supplier-register">공급사 등록하기</RouterLink>
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

const valueCards = [
  {
    icon: "01",
    title: "검증된 데이터",
    description: "공급사 실적과 표준 기준을 함께 확인합니다.",
  },
  {
    icon: "02",
    title: "정확한 추천",
    description: "물성 동등성과 납품 조건을 기준으로 후보를 줄입니다.",
  },
  {
    icon: "03",
    title: "현장 중심 추정",
    description: "현장 위치 기준으로 거리와 문의 우선순위를 비교합니다.",
  },
  {
    icon: "04",
    title: "빠른 의사결정",
    description: "복잡한 전화 확인 전, 먼저 볼 후보를 정리합니다.",
  },
];

const workflowCards = [
  {
    step: "01",
    title: "기준 자재 입력",
    description: "자재명, 규격, 강도 등급, 현장 주소를 입력해 비교 기준을 만듭니다.",
    visualType: "visual-document",
  },
  {
    step: "02",
    title: "대체 후보 선별",
    description: "물성 기준과 납품 조건을 통과한 공급사 후보만 추천 목록에 남깁니다.",
    visualType: "visual-shield",
  },
  {
    step: "03",
    title: "문의 우선순위 확인",
    description: "가격, 거리, 납품 이력, 승인 리스크를 비교해 먼저 연락할 곳을 정합니다.",
    visualType: "visual-ranking",
  },
];

const materialProof = {
  original: {
    name: "철근 SD400 D10",
    maker: "A사",
    registeredAt: "2024.05.20",
    visualClass: "material-visual-rebar",
  },
  candidate: {
    name: "철근 SD400 D10",
    maker: "B사",
    registeredAt: "2024.05.18",
    visualClass: "material-visual-rebar",
  },
};

const materialComparisonRows = [
  { label: "항복강도 (MPa)", original: "400 이상", candidate: "420", result: "동등" },
  { label: "인장강도 (MPa)", original: "560 이상", candidate: "580", result: "동등" },
  { label: "연신율 (%)", original: "16 이상", candidate: "18", result: "동등" },
  { label: "단위중량 (kg/m)", original: "0.617", candidate: "0.617", result: "동등" },
];

const reasonCards = [
  {
    label: "현장까지 가까운 거리",
    value: "4.8 km",
    description: "현장 기준 가까운 공급사를 우선 비교합니다.",
  },
  {
    label: "경쟁력 있는 단가",
    value: "-7.3%",
    description: "기준 자재 대비 평균 단가 절감 가능성을 확인합니다.",
  },
  {
    label: "신뢰할 수 있는 납품 이력",
    value: "최근 36건",
    description: "최근 납품 실적을 신뢰도 근거로 반영합니다.",
  },
];

const scopeItems = [
  "문의 및 연락은 사용자가 직접 진행합니다.",
  "계약 및 거래는 기존 방식 그대로 진행합니다.",
  "더 빠른 방식으로 의사결정 시간을 줄입니다.",
];

const isSupplier = computed(() => authState.user?.role === "supplier");
const roleLabel = computed(() => (isSupplier.value ? "Supplier" : "Requester"));
const approvalCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.supplier?.approvalRequired).length,
);
const roleHeadline = computed(() =>
  isSupplier.value ? "등록 자재와 문의를 관리하세요." : "요청과 문의 상태를 확인하세요.",
);
const roleDescription = computed(() =>
  isSupplier.value
    ? "취급 자재를 등록하고 접수 문의의 공급 가능 여부를 업데이트할 수 있습니다."
    : "새 자재 요청을 등록하고 추천 후보에 남긴 문의 상태를 이어서 확인할 수 있습니다.",
);
const roleStats = computed(() => {
  if (isSupplier.value) {
    return [
      { label: "등록 자재", value: `${supplierMaterials.value.length}개` },
      { label: "접수 문의", value: `${inquiries.value.length}건` },
    ];
  }

  return [
    { label: "저장 문의", value: `${inquiries.value.length}건` },
    { label: "승인 확인", value: `${approvalCount.value}건` },
  ];
});
const primaryRoleAction = computed(() =>
  isSupplier.value
    ? { label: "취급 자재 등록", to: "/supplier-register" }
    : { label: "자재 요청하기", to: "/request" },
);
const secondaryRoleAction = computed(() =>
  isSupplier.value
    ? { label: "문의 관리", to: "/dashboard" }
    : { label: "문의 내역", to: "/dashboard" },
);
const dockLink = computed(() => {
  if (!authState.user) {
    return { label: "공급사 등록 안내", to: "/login?role=supplier" };
  }

  return isSupplier.value
    ? { label: "공급사 자재 등록", to: "/supplier-register" }
    : { label: "내 문의 내역", to: "/dashboard" };
});
const searchButtonLabel = computed(() => (isSupplier.value ? "추천 후보 보기" : "대체 자재 찾기"));

onMounted(() => {
  loadRoleSummary();
  revealObservedSections();
});

function revealObservedSections() {
  const sections = document.querySelectorAll(".section-observe");

  if (!("IntersectionObserver" in window)) {
    sections.forEach((section) => section.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.18 },
  );

  sections.forEach((section) => observer.observe(section));
}

async function loadRoleSummary() {
  if (!authState.user) {
    return;
  }

  try {
    isLoading.value = true;
    errorMessage.value = "";
    inquiries.value = await getSupplierInquiries();

    if (isSupplier.value) {
      supplierMaterials.value = await getSupplierMaterials();
    }
  } catch {
    errorMessage.value = "요약 정보를 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function submitSearch() {
  const query = keyword.value ? { keyword: keyword.value } : {};
  router.push({
    path: isSupplier.value ? "/recommendations" : "/request",
    query,
  });
}
</script>
