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
          부족한 자재를 입력하면 규격, 물성, 거리, 단가, 납품 이력을 비교해 대체 자재와
          공급사 후보를 추천합니다.
        </p>
        <div class="hero-proof-row" aria-label="추천 기준">
          <span>KS·물성 검증</span>
          <span>거리·단가 비교</span>
          <span>납품 이력 기반 추천</span>
        </div>
      </div>

      <form class="hero-search-dock" @submit.prevent="submitSearch">
        <div class="search-field">
          <label for="hero-material-search">자재 검색</label>
          <div class="search-control-row">
            <div class="search-input-area">
              <input
                id="hero-material-search"
                v-model="keyword"
                type="search"
                placeholder="필요한 자재를 입력하세요"
                autocomplete="off"
                role="combobox"
                aria-autocomplete="list"
                aria-controls="material-suggestion-list"
                :aria-expanded="showSuggestionDropdown"
                :aria-activedescendant="activeSuggestionId || undefined"
                @focus="showAvailableSuggestions"
                @blur="hideSuggestions"
                @keydown="handleSearchKeydown"
              />
              <div
                v-if="showSuggestionDropdown"
                id="material-suggestion-list"
                class="material-suggestion-dropdown"
                role="listbox"
              >
                <button
                  v-for="(suggestion, index) in materialSuggestions"
                  :key="`${suggestion.id}-${suggestion.name}-${suggestion.spec}`"
                  :id="`material-suggestion-${index}`"
                  :class="{ 'is-active': index === activeSuggestionIndex }"
                  type="button"
                  role="option"
                  :aria-selected="index === activeSuggestionIndex"
                  @mouseenter="activeSuggestionIndex = index"
                  @mousedown.prevent="selectSuggestion(suggestion)"
                >
                  <span class="suggestion-copy">
                    <span class="suggestion-main">
                      <strong>{{ suggestion.name }}</strong>
                      <small v-if="suggestion.spec">{{ suggestion.spec }}</small>
                    </span>
                    <span class="suggestion-meta">
                      {{ suggestion.material_group }}
                      <template v-if="suggestion.material_subtype">
                        · {{ suggestion.material_subtype }}
                      </template>
                    </span>
                  </span>
                  <span v-if="suggestion.supplier_name" class="suggestion-supply">
                    {{ suggestion.supplier_name }}
                  </span>
                  <span v-else-if="suggestion.available" class="suggestion-supply">
                    공급 이력 있음
                  </span>
                </button>
              </div>
            </div>
            <button type="submit">{{ searchButtonLabel }}</button>
            <RouterLink class="dock-link" :to="dockLink.to">{{ dockLink.label }}</RouterLink>
          </div>
          <div class="search-example-tags" aria-label="자재 검색 예시">
            <button
              v-for="example in searchExamples"
              :key="example"
              type="button"
              @click="keyword = example"
            >
              {{ example }}
            </button>
          </div>
        </div>
      </form>
    </section>

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

    <div class="sep-home-wrap home-section section-observe">
      <StandardEvidencePanel />
    </div>

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

    <!-- <section class="bottom-cta-section section-observe">
      <div>
        <h2>지금 바로 대체 자재를 검색하고, 최적의 공급사 후보를 확인해보세요.</h2>
      </div>
      <div>
        <RouterLink class="primary-button" to="/recommendations">대체 자재 찾기</RouterLink>
        <RouterLink class="secondary-button" to="/supplier-register">공급사 등록하기</RouterLink>
      </div>
    </section> -->

    <Transition name="top-btn">
      <button v-if="showTop" class="scroll-top-btn" @click="scrollToTop" aria-label="맨 위로">
        ↑
      </button>
    </Transition>
  </div>
</template>

<script setup>
import StandardEvidencePanel from '../components/StandardEvidencePanel.vue'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { authState } from "../api/authApi";
import { getMaterialSuggestions } from "../api/materialApi";

const router = useRouter();
const keyword = ref("");
const materialSuggestions = ref([]);
const suggestionsOpen = ref(false);
const activeSuggestionIndex = ref(-1);
const searchExamples = ["철근 SD400 D10", "H형강 300x300", "고로슬래그 시멘트 1종"];
let suggestionTimer;
let suggestionRequestId = 0;
let suppressNextSuggestionFetch = false;

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
const dockLink = computed(() => {
  if (!authState.user) {
    return { label: "공급사 등록 안내", to: "/login?role=supplier" };
  }

  return isSupplier.value
    ? { label: "공급사 자재 등록", to: "/supplier-register" }
    : { label: "내 문의 내역", to: "/dashboard" };
});
const searchButtonLabel = computed(() => (isSupplier.value ? "추천 후보 보기" : "대체 자재 찾기"));
const showSuggestionDropdown = computed(
  () => suggestionsOpen.value && materialSuggestions.value.length > 0,
);
const activeSuggestionId = computed(() =>
  activeSuggestionIndex.value >= 0
    ? `material-suggestion-${activeSuggestionIndex.value}`
    : "",
);

watch(keyword, (value) => {
  if (suppressNextSuggestionFetch) {
    suppressNextSuggestionFetch = false;
    return;
  }

  clearTimeout(suggestionTimer);
  const query = value.trim();
  if (!query) {
    suggestionRequestId += 1;
    materialSuggestions.value = [];
    suggestionsOpen.value = false;
    activeSuggestionIndex.value = -1;
    return;
  }

  const requestId = ++suggestionRequestId;
  suggestionTimer = setTimeout(async () => {
    try {
      const suggestions = await getMaterialSuggestions(query);
      if (requestId !== suggestionRequestId) {
        return;
      }
      materialSuggestions.value = suggestions;
      suggestionsOpen.value = suggestions.length > 0;
      activeSuggestionIndex.value = -1;
    } catch {
      if (requestId === suggestionRequestId) {
        materialSuggestions.value = [];
        suggestionsOpen.value = false;
        activeSuggestionIndex.value = -1;
      }
    }
  }, 280);
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

function submitSearch() {
  suggestionsOpen.value = false;
  const query = keyword.value ? { keyword: keyword.value } : {};
  router.push({ path: "/recommendations", query });
}

function showAvailableSuggestions() {
  if (keyword.value.trim() && materialSuggestions.value.length) {
    suggestionsOpen.value = true;
  }
}

function hideSuggestions() {
  suggestionsOpen.value = false;
  activeSuggestionIndex.value = -1;
}

function selectSuggestion(suggestion) {
  clearTimeout(suggestionTimer);
  suggestionRequestId += 1;
  suppressNextSuggestionFetch = true;
  keyword.value = [suggestion.name, suggestion.spec].filter(Boolean).join(" ").trim();
  materialSuggestions.value = [];
  suggestionsOpen.value = false;
  activeSuggestionIndex.value = -1;
}

function handleSearchKeydown(event) {
  if (event.key === "ArrowDown") {
    event.preventDefault();
    moveSuggestion(1);
    return;
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    moveSuggestion(-1);
    return;
  }

  if (event.key === "Enter" && showSuggestionDropdown.value && activeSuggestionIndex.value >= 0) {
    event.preventDefault();
    selectSuggestion(materialSuggestions.value[activeSuggestionIndex.value]);
    return;
  }

  if (event.key === "Escape" && showSuggestionDropdown.value) {
    event.preventDefault();
    suggestionsOpen.value = false;
    activeSuggestionIndex.value = -1;
  }
}

function moveSuggestion(direction) {
  const suggestionCount = materialSuggestions.value.length;
  if (!suggestionCount) {
    return;
  }

  suggestionsOpen.value = true;
  if (activeSuggestionIndex.value < 0) {
    activeSuggestionIndex.value = direction > 0 ? 0 : suggestionCount - 1;
  } else {
    activeSuggestionIndex.value =
      (activeSuggestionIndex.value + direction + suggestionCount) % suggestionCount;
  }

  nextTick(() => {
    document
      .getElementById(activeSuggestionId.value)
      ?.scrollIntoView({ block: "nearest" });
  });
}

// 스크롤 상단 버튼
const showTop = ref(false);

function onScroll() {
  showTop.value = window.scrollY > 400;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => {
  revealObservedSections();
  window.addEventListener("scroll", onScroll, { passive: true });
});

onBeforeUnmount(() => {
  clearTimeout(suggestionTimer);
  suggestionRequestId += 1;
  window.removeEventListener("scroll", onScroll);
});
</script>

<style scoped>
.scroll-top-btn {
  position: fixed;
  right: 32px;
  bottom: 36px;
  z-index: 90;
  width: 48px;
  height: 48px;
  border: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #1559e8, #1f8df2);
  color: #fff;
  font-size: 20px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 8px 28px rgba(21, 89, 232, 0.36);
  transition: transform 0.18s, box-shadow 0.18s;
}

.scroll-top-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 36px rgba(21, 89, 232, 0.44);
}

.top-btn-enter-active,
.top-btn-leave-active {
  transition: opacity 0.22s, transform 0.22s;
}

.top-btn-enter-from,
.top-btn-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
