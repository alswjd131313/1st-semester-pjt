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

    <section class="operations-section section-observe">
      <div class="section-heading compact-heading">
        <p class="eyebrow">Field Workflow</p>
        <h2>자재 수급 이슈를 한 흐름으로 정리합니다.</h2>
      </div>

      <div class="workflow-grid">
        <article v-for="item in workflowCards" :key="item.title">
          <span>{{ item.step }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="evidence-section section-observe">
      <div class="section-heading compact-heading">
        <p class="eyebrow">Recommendation Evidence</p>
        <h2>추천 이유가 보이는 공급사 비교</h2>
      </div>

      <div class="evidence-layout">
        <article class="evidence-feature">
          <span>추천 기준</span>
          <strong>규격부터 문의 우선순위까지</strong>
          <p>
            PaceFlow는 실시간 거래를 대신하지 않습니다. 대신 현장 담당자가 빠르게
            판단할 수 있도록 후보의 근거와 한계를 함께 보여줍니다.
          </p>
        </article>

        <div class="evidence-grid">
          <article v-for="item in evidenceCards" :key="item.title">
            <span>{{ item.label }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="service-scope-section section-observe">
      <div>
        <p class="eyebrow">Service Scope</p>
        <h2>구매 확정이 아니라, 더 빠른 문의 결정을 돕습니다.</h2>
      </div>
      <ul>
        <li v-for="item in scopeItems" :key="item">{{ item }}</li>
      </ul>
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

const workflowCards = [
  {
    step: "01",
    title: "기준 자재 입력",
    description: "자재명, 규격, 강도 등급, 현장 주소를 입력해 비교 기준을 만듭니다.",
  },
  {
    step: "02",
    title: "대체 후보 선별",
    description: "물성 기준과 납품 조건을 통과한 공급사 후보만 추천 목록에 남깁니다.",
  },
  {
    step: "03",
    title: "문의 우선순위 확인",
    description: "가격, 거리, 납품 이력, 승인 리스크를 비교해 먼저 연락할 곳을 정합니다.",
  },
];

const evidenceCards = [
  {
    label: "Spec",
    title: "물성 기준 검토",
    description: "KS 규격뿐 아니라 강도 등급과 주요 물성 조건을 함께 확인합니다.",
  },
  {
    label: "Route",
    title: "현장 기준 거리 비교",
    description: "현장 주소와 공급사 위치를 기준으로 접근성과 납품 부담을 비교합니다.",
  },
  {
    label: "Record",
    title: "납품 이력 기반 신뢰도",
    description: "공급사 등록 정보와 계약 이력을 구분해 추천 근거로 표시합니다.",
  },
];

const scopeItems = [
  "실시간 재고 보장은 하지 않으며 최종 납품 가능 여부는 공급사 확인이 필요합니다.",
  "요청자와 공급사는 로그인 역할에 따라 필요한 기능만 우선 노출됩니다.",
  "지도와 주소 정보는 현장 기준 거리 비교와 공급사 위치 확인에 활용됩니다.",
];

const isSupplier = computed(() => authState.user?.role === "supplier");
const isRequester = computed(() => authState.user?.role === "requester");
const roleLabel = computed(() => (isSupplier.value ? "Supplier" : "Requester"));
const quotedCount = computed(
  () => inquiries.value.filter((inquiry) => inquiry.status === "quoted").length,
);
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
