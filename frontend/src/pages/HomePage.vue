<template>
  <div class="home-page">
    <section class="hero-section pace-hero section-observe">

      <div class="pace-hero-copy">
        <p class="eyebrow">PaceFlow Material Intelligence</p>
        <h1>
          <span>대체 자재 추천부터</span>
          <span>공급사 문의까지, 더 빠르게</span>
        </h1>
        <p class="hero-description">
          KS 규격·물성 데이터와 공급사 납품 이력을 자동 비교해 현장 위치·단가 기준으로 우선 문의할 후보를 즉시 추천합니다.
        </p>
        <div class="hero-proof-row" aria-label="추천 기준">
          <span>물성 기준 검토</span>
          <span>거리·단가 비교</span>
          <span>납품 이력 반영</span>
        </div>
      </div>

      <form class="hero-search-dock" @submit.prevent="submitSearch">
        <p class="dock-title">자재 검색</p>
        <div class="dock-row">
          <div class="dock-input-wrap">
            <input
              v-model="keyword"
              type="text"
              placeholder="필요한 자재를 입력하세요"
              autocomplete="off"
              @focus="showAc = true"
              @blur="hideAc"
              @keydown.arrow-down.prevent="acMove(1)"
              @keydown.arrow-up.prevent="acMove(-1)"
              @keydown.enter.prevent="onAcEnter"
              @keydown.esc="showAc = false"
              @input="showAc = true; acIndex = -1"
            />
            <ul v-if="showAc && acSuggestions.length" class="ac-list">
              <li
                v-for="(s, i) in acSuggestions"
                :key="s"
                :class="{ 'ac-active': i === acIndex }"
                @mousedown.prevent="selectAc(s)"
              >
                <span class="ac-icon">🔍</span>{{ s }}
              </li>
            </ul>
          </div>
          <button type="submit">대체 자재 찾기</button>
          <RouterLink class="dock-link" to="/login?role=supplier">공급사 등록 안내</RouterLink>
        </div>
        <div class="dock-tags">
          <button type="button" class="dock-tag" @click="fillTag('철근 SD400 D10')">철근 SD400 D10</button>
          <button type="button" class="dock-tag" @click="fillTag('H형강 300x300')">H형강 300x300</button>
          <button type="button" class="dock-tag" @click="fillTag('고로슬래그 시멘트 1종')">고로슬래그 시멘트 1종</button>
        </div>
      </form>
    </section>
      <StandardEvidencePanel />

    <section class="value-strip section-observe">
      <div class="section-heading center-heading">
        <h2>자재 수급 업무를 <span>더 간단하게</span></h2>
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
        <h2>3단계로 끝나는 자재 탐색</h2>
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
        <h2>현장 의사결정을 위한 추천 플랫폼</h2>
        <p>
          PaceFlow는 자재 구매 과정에서 필요한 공급사 탐색과 비교 업무를 간소화합니다. 여러 공급사를 직접 찾고 비교하던 과정을 몇 분 안에 끝낼 수 있도록 지원합니다. 현장 담당자가 여러 공급사를 탐색하고
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
        <RouterLink class="primary-button" to="/recommendations">대체 자재 찾기</RouterLink>
        <RouterLink class="secondary-button" to="/supplier-register">공급사 등록하기</RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import StandardEvidencePanel from '../components/StandardEvidencePanel.vue'
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { authState } from "../api/authApi";
import { getSupplierInquiries, getSupplierMaterials } from "../api/materialApi";

const router = useRouter();

// 자동완성
const showAc = ref(false);
const acIndex = ref(-1);

const AC_DATA = [
  "철근 SD300 D10", "철근 SD300 D13", "철근 SD300 D16",
  "철근 SD400 D10", "철근 SD400 D13", "철근 SD400 D16", "철근 SD400 D19", "철근 SD400 D22", "철근 SD400 D25",
  "철근 SD500 D13", "철근 SD500 D16", "철근 SD500 D19", "철근 SD500 D22", "철근 SD500 D25", "철근 SD500 D29",
  "철근 SD600 D16", "철근 SD600 D19", "철근 SD600 D22", "철근 SD600 D25",
  "H형강 100x100", "H형강 150x150", "H형강 200x200", "H형강 250x250", "H형강 300x300", "H형강 350x350", "H형강 400x400",
  "I형강 100x50", "I형강 150x75", "I형강 200x100",
  "ㄷ형강 75x40", "ㄷ형강 100x50", "ㄷ형강 150x65",
  "ㄱ형강 50x50x6", "ㄱ형강 75x75x6", "ㄱ형강 100x100x7",
  "포틀랜드 시멘트 1종", "포틀랜드 시멘트 2종", "포틀랜드 시멘트 3종",
  "고로슬래그 시멘트 1종", "고로슬래그 시멘트 2종", "백시멘트",
  "EPS 단열재 1종 50t", "EPS 단열재 2종 100t", "XPS 단열재 50t", "XPS 단열재 100t",
  "우레탄폼 단열재 50t", "경질 우레탄폼 단열재 80t",
  "합판 12mm", "합판 15mm", "합판 18mm", "합판 24mm",
  "각재 30x40", "각재 40x60", "각재 50x100",
];

const acSuggestions = computed(() => {
  const kw = keyword.value.trim().toLowerCase();
  if (!kw) return [];
  return AC_DATA.filter((s) => s.toLowerCase().includes(kw)).slice(0, 8);
});

function hideAc() {
  setTimeout(() => { showAc.value = false; acIndex.value = -1; }, 150);
}

function acMove(dir) {
  showAc.value = true;
  acIndex.value = Math.max(-1, Math.min(acIndex.value + dir, acSuggestions.value.length - 1));
}

function onAcEnter() {
  if (acIndex.value >= 0 && acSuggestions.value[acIndex.value]) {
    selectAc(acSuggestions.value[acIndex.value]);
  } else {
    showAc.value = false;
    submitSearch();
  }
}

function selectAc(text) {
  keyword.value = text;
  showAc.value = false;
  acIndex.value = -1;
}
const keyword = ref("");
const inquiries = ref([]);
const supplierMaterials = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");

const valueCards = [
  {
    icon: "01",
    title: "검증된 공급사 정보 ",
    description: "실제 납품 이력과 표준 규격을 기반으로 신뢰할 수 있는 공급사를 찾습니다.",
  },
  {
    icon: "02",
    title: "대체 가능 자재 자동 검토",
    description: "복잡한 규격과 물성 조건을 비교해 대체 가능한 후보를 선별합니다.",
  },
  {
    icon: "03",
    title: "현장에 가까운 공급사 우선 추천",
    description: "현장 위치 기준으로 거리와 문의 우선순위를 비교합니다.",
  },
  {
    icon: "04",
    title: "빠른 의사결정",
    description: "여러 업체를 직접 비교하는 시간을 줄이고 필요한 자재를 빠르게 확보합니다.",
  },
];

const workflowCards = [
  {
    step: "01",
    title: "자재와 현장 정보 입력",
    description: "찾고 있는 자재와 현장 정보를 입력하면 비교 기준이 자동으로 설정됩니다.",
    visualType: "visual-document",
  },
  {
    step: "02",
    title: "대체 가능 후보 자동 검토",
    description: "규격과 물성 조건을 분석해 적용 가능한 자재와 공급사를 선별합니다.",
    visualType: "visual-shield",
  },
  {
    step: "03",
    title: "문의 우선순위 확인",
    description: "거리, 단가, 납품 실적을 종합해 우선 연락할 업체를 정리합니다.",
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
    description: "현장과 가까운 공급사를 우선 추천해 운송 부담을 줄입니다.",
  },
  {
    label: "경쟁력 있는 단가",
    value: "-7.3%",
    description: "기존 자재 대비 비용 절감 가능성이 높은 후보입니다.",
  },
  {
    label: "신뢰할 수 있는 납품 이력",
    value: "최근 36건",
    description: "실제 납품 이력을 바탕으로 공급 안정성을 평가합니다.",
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
  router.push({ path: "/recommendations", query });
}

function fillTag(text) {
  keyword.value = text;
}
</script>
