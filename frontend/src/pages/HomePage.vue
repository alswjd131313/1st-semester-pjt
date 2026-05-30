<template>
  <section class="hero-section">
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
      <span>누적 구현 상태</span>
      <strong>요청부터 상세 확인까지</strong>
      <p>로그인, 자재 요청, 공급사 등록, 추천 결과, 상세 보기 흐름을 한 번에 확인할 수 있습니다.</p>
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
