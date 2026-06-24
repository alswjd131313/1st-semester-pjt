<template>
  <div class="home-page">
    <section class="hero-section pace-hero section-observe">

      <div class="pace-hero-copy">
        <p class="eyebrow">Construction Supply Platform</p>
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

      <form v-if="!isSupplier" class="hero-search-dock" @submit.prevent="submitSearch">
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

      <section v-else class="hero-search-dock supplier-work-dock" aria-labelledby="supplier-work-title">
        <div class="supplier-work-copy">
          <div>
            <p class="supplier-work-eyebrow">Supplier Workspace</p>
            <h2 id="supplier-work-title">공급사 업무 바로가기</h2>
            <p>등록한 취급 자재를 관리하고, 요청자가 보낸 자재 문의에 응답하세요.</p>
          </div>
          <div class="supplier-work-actions">
            <RouterLink class="supplier-action supplier-action-primary" :to="{ name: 'inquiries' }">
              받은 요청 확인
            </RouterLink>
            <RouterLink class="supplier-action supplier-action-secondary" :to="{ name: 'supplier-profile' }">
              자재 관리하기
            </RouterLink>
          </div>
        </div>

        <div class="supplier-work-stats" aria-label="공급사 업무 현황">
          <article v-for="stat in supplierStats" :key="stat.label">
            <span>{{ stat.label }}</span>
            <strong>{{ stat.value }}{{ stat.unit }}</strong>
          </article>
        </div>
      </section>
    </section>

    <section class="value-strip" ref="valueStripRef">
      <div class="value-sticky">
        <div class="value-head">
          <h2>자재 수급 업무를 <span>더 간단하게</span></h2>
        </div>
        <div class="value-scene">
          <div
            v-for="(card, i) in valueCards"
            :key="i"
            :class="['vc', getVcClass(i)]"
          >
            <div class="vc-front">
              <div class="vc-icon" v-html="card.icon"></div>
              <span class="vc-front-num">{{ String(i + 1).padStart(2, '0') }}</span>
              <span class="vc-front-title">{{ card.headline }}</span>
            </div>
            <div class="vc-overlay">
              <h3>{{ card.headline }}</h3>
              <div class="vc-divider-line"></div>
              <p>{{ card.description }}</p>
            </div>
          </div>
        </div>
        <div class="vc-dots">
          <span
            v-for="(_, i) in valueCards"
            :key="i"
            :class="['vc-dot', { 'vc-dot-active': i === vcActive }]"
          ></span>
        </div>
      </div>
    </section>

    <section class="flow-section section-observe">
      <div class="section-heading center-heading">
        <h2><span>3단계</span>로 끝나는 자재 탐색</h2>
      </div>

      <div class="flow-card-grid">
        <article v-for="item in workflowCards" :key="item.title">
          <span class="flow-step">{{ item.step }}</span>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
          <img class="flow-visual-img" :src="item.image" :alt="item.title" aria-hidden="true" />
        </article>
      </div>
    </section>

    <section class="material-proof-section section-observe">
      <div class="section-heading center-heading">
        <h2>예시로 보는 <span>물성 비교</span></h2>
        <p class="mp-section-sub">AI가 분석한 두 자재의 물성 데이터 비교 결과입니다.</p>
      </div>

      <div class="mp-wrap">
        <!-- 두 자재 헤더 -->
        <div class="mp-mat-header">
          <div class="mp-mat-card">
            <span class="mp-mat-badge mp-badge-blue">원본 자재</span>
            <h3>{{ materialProof.original.name }}</h3>
          </div>
          <div class="mp-arrow-ring">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M5 12h14M14 7l5 5-5 5" stroke="#1559e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="mp-mat-card mp-mat-card-right">
            <span class="mp-mat-badge mp-badge-green">추천 자재</span>
            <h3>{{ materialProof.candidate.name }}</h3>
          </div>
        </div>

        <!-- 비교 테이블 -->
        <div class="mp-table">
          <div class="mp-row mp-head">
            <span>항목</span>
            <span>원본 자재 ({{ materialProof.original.code }})</span>
            <span>추천 자재 ({{ materialProof.candidate.code }})</span>
            <span>비교 결과</span>
          </div>
          <div v-for="row in materialComparisonRows" :key="row.label" class="mp-row">
            <span class="mp-label-cell">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z" fill="#dbeafe" stroke="#1559e8" stroke-width="1.6"/>
              </svg>
              {{ row.label }}
            </span>
            <span>{{ row.original }}</span>
            <span>{{ row.candidate }}</span>
            <span class="mp-result-cell">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="#16a34a" stroke-width="1.8"/>
                <path d="M8 12l3 3 5-5" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              동등
            </span>
          </div>
        </div>

        <!-- 결과 배너 -->
        <div class="mp-verdict-banner">
          <div class="mp-verdict-left">
            <div class="mp-verdict-icon">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="11" fill="#16a34a"/>
                <path d="M7 12l4 4 6-6" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <strong class="mp-verdict-title">물성 동등성 검증 완료</strong>
              <p>두 자재의 주요 물성이 동등함을 확인했습니다.</p>
            </div>
          </div>
          <div class="mp-verdict-sep"></div>
          <div class="mp-verdict-tag">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z" stroke="#16a34a" stroke-width="2"/>
            </svg>
            대체 가능
          </div>
        </div>
      </div>
    </section>

    <div class="sep-home-wrap home-section section-observe">
      <StandardEvidencePanel />
    </div>

    <section class="recommend-reason-section section-observe">
      <div class="rr-inner">
        <div class="rr-intro">
          <h2>왜 이 공급사를<br><span>추천할까요?</span></h2>
          <p>다음 3가지 기준을<br>종합적으로 분석하여<br>가장 적합한 공급사를 추천합니다.</p>
        </div>
        <div class="rr-rows">
          <div
            v-for="(item, i) in reasonCards"
            :key="item.title"
            :class="['rr-row', i % 2 !== 0 && 'rr-row-flip']"
          >
            <img :src="item.image" :alt="item.title" class="rr-img" />
            <div class="rr-content">
              <span class="rr-num">{{ item.num }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <div class="rr-criteria">
                <span class="rr-criteria-label">분석 기준</span>
                <ul>
                  <li v-for="c in item.criteria" :key="c">{{ c }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="service-scope-section section-observe">
      <div class="brand-cta-wrap">
        <p class="brand-cta-eyebrow">PaceFlow</p>
        <h2>자재 조달의 새로운 기준을<br><span>경험해보세요</span></h2>
        <p class="brand-cta-desc">
          KS 규격 비교, 물성 검토, 공급사 추천까지 — PaceFlow 하나로 해결합니다.<br>
          현장 담당자가 직접 탐색하던 과정을 몇 분 안에 끝낼 수 있습니다.
        </p>
        <div class="brand-cta-actions">
          <RouterLink class="brand-btn brand-btn-primary" to="/materials/request">대체 자재 검색하기</RouterLink>
          <button class="brand-btn brand-btn-secondary" type="button" @click="handleSupplierCta">공급사로 참여하기</button>
        </div>
        <p v-if="supplierCtaNotice" class="supplier-cta-notice">{{ supplierCtaNotice }}</p>
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

    <footer class="home-footer section-observe">
      <div class="footer-inner">
        <nav class="footer-nav">
          <span class="footer-nav-brand">PaceFlow</span>
          <span class="footer-nav-item">자재 수급 자동화 플랫폼</span>
          <span class="footer-nav-item">SSAFY 15기 1학기 프로젝트</span>
          <span class="footer-nav-item">건설 현장 자재 추천 서비스</span>
        </nav>

        <div class="footer-team">
          <div class="footer-team-row">
            <span class="ft-label">팀원</span>
            <span class="ft-name">장우창</span>
            <span class="ft-badge">SSAFY 15기</span>
            <span class="ft-sep">·</span>
            <span class="ft-email">woo4227@naver.com</span>
          </div>
          <div class="footer-team-row">
            <span class="ft-label">&nbsp;</span>
            <span class="ft-name">황민정</span>
            <span class="ft-badge">SSAFY 15기</span>
            <span class="ft-sep">·</span>
            <span class="ft-email">alswjd131313@naver.com</span>
          </div>
        </div>

        <div class="footer-bottom">
          <span>© 2025. PaceFlow. Built with SSAFY 15기.</span>
        </div>
      </div>
    </footer>

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
import { authState, isLoggedIn } from "../api/authApi";
import {
  getMaterialSuggestions,
  filterInquiriesForUser,
  getSupplierInquiries,
  getSupplierMaterials,
} from "../api/materialApi";

const router = useRouter();
const keyword = ref("");
const materialSuggestions = ref([]);
const suggestionsOpen = ref(false);
const activeSuggestionIndex = ref(-1);
const searchExamples = ["철근 SD400 D10", "H형강 300x300", "고로슬래그 시멘트 1종"];
let suggestionTimer;
let suggestionRequestId = 0;
let suppressNextSuggestionFetch = false;

const valueStripRef = ref(null);
const vcActive = ref(0);

function getVcClass(i) {
  const diff = i - vcActive.value;
  if (diff === 0) return "vc-active";
  if (diff === -1) return "vc-prev";
  if (diff === 1) return "vc-next";
  if (diff > 1) return "vc-upcoming";
  return "vc-past";
}

const valueCards = [
  {
    headline: '규격 적합성 검토',
    description: 'KS 및 국제 규격을 기준으로\n강도 등급, 치수, 허용 오차 등 규격 적합성을 자동으로 검토합니다.',
    icon: `<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="5" width="37" height="49" rx="4" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M33 5v12h12" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><rect x="8" y="5" width="37" height="14" rx="4" fill="currentColor" opacity="0.1"/><line x1="16" y1="28" x2="34" y2="28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="16" y1="35" x2="34" y2="35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="16" y1="42" x2="26" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="51" cy="51" r="12" stroke="currentColor" stroke-width="2" fill="currentColor" opacity="0.09"/><path d="M46 51l3.5 3.5 7.5-7.5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  },
  {
    headline: '물성 자동 비교',
    description: '항복강도, 인장강도, 연신율 등 핵심 물성 데이터를 자동으로 비교해 대체 가능성을 판단합니다.',
    icon: `<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="32" cy="32" r="5" fill="currentColor"/><circle cx="32" cy="32" r="10" fill="currentColor" opacity="0.12"/><ellipse cx="32" cy="32" rx="24" ry="9" stroke="currentColor" stroke-width="2.2"/><ellipse cx="32" cy="32" rx="24" ry="9" transform="rotate(60 32 32)" stroke="currentColor" stroke-width="2.2"/><ellipse cx="32" cy="32" rx="24" ry="9" transform="rotate(120 32 32)" stroke="currentColor" stroke-width="2.2"/><circle cx="56" cy="32" r="3.5" fill="currentColor"/><circle cx="20.4" cy="43.5" r="3.5" fill="currentColor"/><circle cx="43.6" cy="20.5" r="3.5" fill="currentColor"/></svg>`,
  },
  {
    headline: '현장 기반 추천',
    description: '현장 위치를 기준으로 거리와 운송 비용을 고려해 현실적으로 납품 가능한 공급사를 우선 추천합니다.',
    icon: `<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="32" cy="27" r="20" stroke="currentColor" stroke-width="1.5" opacity="0.18" stroke-dasharray="4 3"/><path d="M32 8C21.5 8 13 16.5 13 27c0 15 19 29 19 29s19-14 19-29C51 16.5 42.5 8 32 8z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><circle cx="32" cy="27" r="7" stroke="currentColor" stroke-width="2.5"/><circle cx="32" cy="27" r="2.5" fill="currentColor"/></svg>`,
  },
  {
    headline: '검증된 공급사 연결',
    description: '실제 납품 이력과 KS 규격을 갖춘 등록 공급사만을 대상으로 우선 문의할 후보를 선별합니다.',
    icon: `<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><line x1="32" y1="6" x2="32" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M32 6l7 4.5-7 4.5-7-4.5z" fill="currentColor" opacity="0.55"/><rect x="11" y="20" width="42" height="38" rx="2" stroke="currentColor" stroke-width="2.5"/><line x1="11" y1="30" x2="53" y2="30" stroke="currentColor" stroke-width="1.5"/><rect x="17" y="22" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="29" y="22" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="41" y="22" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="17" y="34" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="41" y="34" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="27" y="44" width="11" height="14" rx="2" stroke="currentColor" stroke-width="2"/></svg>`,
  },
];

const workflowCards = [
  {
    step: "01",
    title: "자재와 현장 정보 입력",
    description: "찾고 있는 자재와 현장 정보를 입력하면 비교 기준이 자동으로 설정됩니다.",
    image: "/step_01.png",
  },
  {
    step: "02",
    title: "대체 가능 후보 자동 검토",
    description: "규격과 물성 조건을 분석해 적용 가능한 자재와 공급사를 선별합니다.",
    image: "/step_02.png",
  },
  {
    step: "03",
    title: "문의 우선순위 확인",
    description: "거리, 단가, 납품 실적을 종합해 우선 연락할 업체를 정리합니다.",
    image: "/step_03.png",
  },
];

const materialProof = {
  original: {
    name: "철근 SD400 D10",
    code: "SD400 D10",
    maker: "A사",
    registeredAt: "2024.05.20",
    visualClass: "material-visual-rebar",
  },
  candidate: {
    name: "철근 SD500 D10",
    code: "SD500 D10",
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
    num: '01',
    title: '현장과 가까운 거리',
    description: '현장 위치를 기준으로 거리를 계산하여 운송 효율이 높은 공급사를 우선 추천합니다.',
    criteria: ['현장 주소 좌표', '공급사 사업장 위치', '실제 이동 가능 경로 및 거리'],
    image: '/construction_01.png',
  },
  {
    num: '02',
    title: '경쟁력 있는 단가',
    description: '최근 거래 가격 데이터를 기반으로 비용 경쟁력이 높은 공급사를 추천합니다.',
    criteria: ['최근 거래 단가 및 견적 데이터', '자재 규격 및 수량 기준 가격 비교', '시장 평균 대비 비용 경쟁력'],
    image: '/construction_02.png',
  },
  {
    num: '03',
    title: '신뢰할 수 있는 납품 이력',
    description: '실제 납품 및 거래 이력을 기반으로 납품 안정성이 높은 공급사를 추천합니다.',
    criteria: ['최근 납품 건수 및 납품 빈도', '납기 준수율 및 약속 이행도', '거래 이력 및 고객 만족도'],
    image: '/construction_03.png',
  },
];


const isSupplier = computed(() => authState.user?.role === "supplier");
const supplierStats = ref([
  { label: "확인 대기 요청", value: 0, unit: "건" },
  { label: "등록 자재", value: 0, unit: "개" },
  { label: "응답 완료", value: 0, unit: "건" },
]);
const pendingInquiryStatuses = new Set(["pending", "received", "reviewing"]);
const completedInquiryStatuses = new Set(["accepted", "rejected", "quoted", "unavailable"]);

async function loadSupplierStats() {
  try {
    const [inquiryResult, materialResult] = await Promise.all([
      getSupplierInquiries(),
      getSupplierMaterials(),
    ]);
    const inquiries = filterInquiriesForUser(
      Array.isArray(inquiryResult) ? inquiryResult : [],
      authState.user,
    );
    const materials = Array.isArray(materialResult) ? materialResult : [];

    supplierStats.value = [
      {
        label: "확인 대기 요청",
        value: inquiries.filter((item) => pendingInquiryStatuses.has(item?.status)).length,
        unit: "건",
      },
      { label: "등록 자재", value: materials.length, unit: "개" },
      {
        label: "응답 완료",
        value: inquiries.filter((item) => completedInquiryStatuses.has(item?.status)).length,
        unit: "건",
      },
    ];
  } catch {
    supplierStats.value = [
      { label: "확인 대기 요청", value: 0, unit: "건" },
      { label: "등록 자재", value: 0, unit: "개" },
      { label: "응답 완료", value: 0, unit: "건" },
    ];
  }
}

watch(
  isSupplier,
  (supplierMode) => {
    if (supplierMode) {
      loadSupplierStats();
    }
  },
  { immediate: true },
);

const dockLink = computed(() => {
  if (!authState.user) {
    return { label: "공급사 등록 안내", to: "/login?role=supplier" };
  }

  return isSupplier.value
    ? { label: "공급사 자재 등록", to: "/supplier-register" }
    : { label: "내 문의 내역", to: "/inquiries" };
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

  if (valueStripRef.value) {
    const rect = valueStripRef.value.getBoundingClientRect();
    const totalScroll = valueStripRef.value.offsetHeight - window.innerHeight;
    if (totalScroll > 0) {
      const scrolled = Math.max(0, -rect.top);
      const progress = scrolled / totalScroll;
      vcActive.value = Math.min(
        valueCards.length - 1,
        Math.floor(progress * valueCards.length),
      );
    }
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

const supplierCtaNotice = ref("");
let ctaNoticeTimer;

function handleSupplierCta() {
  if (!isLoggedIn()) {
    router.push("/login?role=supplier");
    return;
  }
  if (authState.user?.role === "supplier") {
    router.push("/dashboard");
    return;
  }
  supplierCtaNotice.value = "공급사 참여는 별도 공급사 계정이 필요합니다. 공급사로 회원가입해 주세요.";
  clearTimeout(ctaNoticeTimer);
  ctaNoticeTimer = setTimeout(() => { supplierCtaNotice.value = ""; }, 5000);
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
.supplier-cta-notice { margin-top: 12px; font-size: 13px; color: #9a5b00; background: #fff8e6; border: 1px solid #f6d860; border-radius: 8px; padding: 10px 16px; text-align: center; }

.supplier-work-dock {
  display: grid !important;
  gap: 22px;
  padding: 26px 28px 24px !important;
}

.supplier-work-copy {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 28px;
}

.supplier-work-eyebrow {
  margin: 0 0 7px;
  color: #1559e8;
  font-size: 1px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.supplier-work-copy h2 {
  margin: 0;
  color: #102a56;
  font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 700;
  letter-spacing: -0.05em;
}

.supplier-work-copy p:last-child {
  margin: 9px 0 0;
  color: #63748d;
  font-size: 15px;
  line-height: 1.6;
}

.supplier-work-actions {
  display: grid;
  grid-template-columns: repeat(2, max-content);
  gap: 10px;
}

.supplier-action {
  display: inline-flex;
  min-height: 52px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 0 22px;
  font-size: 15px;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.supplier-action:hover {
  transform: translateY(-2px);
}

.supplier-action-primary {
  color: #fff;
  background: linear-gradient(135deg, #1559e8, #1f8df2);
  box-shadow: 0 10px 24px rgba(21, 89, 232, 0.2);
}

.supplier-action-secondary {
  border: 1px solid #c8d8f2;
  color: #1559e8;
  background: #fff;
}

.supplier-action-secondary:hover {
  border-color: #7ca7e8;
  box-shadow: 0 8px 20px rgba(36, 81, 142, 0.1);
}

.supplier-work-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.supplier-work-stats article {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid #dce7f7;
  border-radius: 14px;
  padding: 15px 18px;
  background: linear-gradient(145deg, #f8fbff, #f2f7ff);
}

.supplier-work-stats span {
  color: #60738e;
  font-size: 15px;
  font-weight: 700;
}

.supplier-work-stats strong {
  color: #1559e8;
  font-size: 21px;
  font-weight: 900;
  white-space: nowrap;
}

@media (max-width: 820px) {
  .supplier-work-copy {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .supplier-work-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .supplier-work-dock {
    padding: 22px 18px !important;
  }

  .supplier-work-actions,
  .supplier-work-stats {
    grid-template-columns: 1fr;
  }
}

/* ── 스크롤 스티키 카드 섹션 ── */
.value-strip {
  height: 280vh;
  background: linear-gradient(180deg, #e0eaf8 0%, #d8e6f5 100%) !important;
  position: relative;
}

.value-sticky {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 28px;
  overflow: hidden;
}

.value-head {
  text-align: center;
  z-index: 5;
}

.value-head h2 {
  margin: 0;
  color: #102a56;
  font-size: clamp(28px, 3.2vw, 42px);
  font-weight: 800;
  line-height: 1.2;
}

.value-head h2 span {
  color: #1559e8;
}

.value-scene {
  position: relative;
  width: 100%;
  height: 480px;
}

/* ── 카드 (공통) ── */
.vc {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300px;
  height: 430px;
  border-radius: 28px;
  overflow: hidden;
  transition:
    transform 0.6s cubic-bezier(0.32, 0.96, 0.58, 1),
    opacity 0.5s ease,
    box-shadow 0.5s ease;
}

/* ── 앞면 (아이콘 + 라벨) ── */
.vc-front {
  position: absolute;
  inset: 0;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 36px 28px;
}

.vc-icon {
  color: #1559e8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}

.vc-icon svg {
  width: 72px;
  height: 72px;
}

.vc-front-num {
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
  color: #b0c4de;
}

.vc-front-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a6e;
  text-align: center;
  line-height: 1.4;
}

/* ── 어두운 오버레이 (텍스트) ── */
.vc-overlay {
  position: absolute;
  inset: 0;
  background: rgba(16, 26, 54, 0.91);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 44px 36px;
  opacity: 0;
  transition: opacity 0.6s ease;
}

.vc-overlay h3 {
  margin: 0 0 16px;
  color: #fff;
  font-size: 26px;
  font-weight: 800;
  line-height: 1.25;
}

.vc-divider-line {
  width: 36px;
  height: 3px;
  background: #1559e8;
  border-radius: 2px;
  margin-bottom: 20px;
}

.vc-overlay p {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 15px;
  line-height: 1.8;
}

/* ── 카드 상태 ── */
.vc-active {
  transform: translate(-50%, -50%) rotate(-3deg);
  z-index: 3;
  box-shadow: 0 48px 120px rgba(15, 25, 55, 0.28);
}

.vc-active .vc-overlay {
  opacity: 1;
}

.vc-prev {
  transform: translate(calc(-50% - 340px), -38%) rotate(-13deg);
  opacity: 0.72;
  z-index: 2;
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.1);
}

.vc-next {
  transform: translate(calc(-50% + 340px), -38%) rotate(11deg);
  opacity: 0.72;
  z-index: 2;
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.1);
}

.vc-upcoming {
  transform: translate(calc(-50% + 540px), -22%) rotate(18deg);
  opacity: 0;
  z-index: 0;
  pointer-events: none;
}

.vc-past {
  transform: translate(calc(-50% - 540px), -22%) rotate(-20deg);
  opacity: 0;
  z-index: 0;
  pointer-events: none;
}

/* ── 진행 점 ── */
.vc-dots {
  display: flex;
  gap: 8px;
  z-index: 5;
}

.vc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c4cfdf;
  transition: background 0.3s, transform 0.3s;
}

.vc-dot-active {
  background: #1559e8;
  transform: scale(1.35);
}

/* ── 브랜드 CTA 섹션 ── */
.service-scope-section {
  position: relative;
  display: flex !important;
  justify-content: center;
  align-items: center;
  text-align: center;
  min-height: 480px;
  background: linear-gradient(140deg, #070f2b 0%, #0e2261 55%, #081833 100%) !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  max-width: none !important;
  margin: 0 !important;
  overflow: hidden;
}

.service-scope-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 30% 50%, rgba(21, 89, 232, 0.25) 0%, transparent 55%),
    radial-gradient(circle at 75% 40%, rgba(26, 180, 220, 0.15) 0%, transparent 45%);
  pointer-events: none;
}

.brand-cta-wrap {
  position: relative;
  z-index: 1;
  max-width: 720px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.brand-cta-eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #5b9cf6;
}

.service-scope-section h2 {
  margin: 0;
  color: #fff !important;
  font-size: clamp(30px, 4vw, 50px) !important;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.04em;
}

.service-scope-section h2 span {
  color: #5b9cf6;
}

.brand-cta-desc {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 16px;
  line-height: 1.8;
  max-width: 560px;
}

.brand-cta-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 8px;
}

.brand-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 50px;
  padding: 0 28px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.18s, box-shadow 0.18s;
}

.brand-btn:hover {
  transform: translateY(-2px);
}

.brand-btn-primary {
  background: #1559e8;
  color: #fff;
  box-shadow: 0 8px 28px rgba(21, 89, 232, 0.45);
}

.brand-btn-primary:hover {
  box-shadow: 0 14px 36px rgba(21, 89, 232, 0.55);
}

.brand-btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.brand-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.14);
}

/* ── 추천 이유 섹션 ── */
.rr-inner {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 80px;
  max-width: 1220px;
  margin: 0 auto;
  align-items: flex-start;
}

.rr-intro {
  position: sticky;
  top: 100px;
}

.rr-intro h2 {
  color: #102a56;
  font-size: clamp(28px, 3.2vw, 42px);
  font-weight: 800;
  margin-bottom: 18px;
}

.rr-intro h2 span {
  color: #1559e8;
}

.rr-intro p {
  color: #65748d;
  font-size: 15px;
  line-height: 1.75;
}

.rr-rows {
  display: flex;
  flex-direction: column;
}

.rr-row {
  display: grid;
  grid-template-areas: "img content";
  grid-template-columns: 1.15fr 1fr;
  gap: 44px;
  align-items: center;
  padding: 44px 0;
  border-top: 1px solid #dce8f4;
}

.rr-row:last-child {
  border-bottom: 1px solid #dce8f4;
}

.rr-row-flip {
  grid-template-areas: "content img";
  grid-template-columns: 1fr 1.15fr;
}

.rr-img {
  grid-area: img;
  width: 100%;
  height: 260px;
  object-fit: cover;
  border-radius: 14px;
  display: block;
}

.rr-content {
  grid-area: content;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rr-num {
  display: block;
  font-size: 30px;
  font-weight: 900;
  color: #1559e8;
  line-height: 1;
  letter-spacing: -0.04em;
  margin-bottom: 4px;
}

.rr-content h3 {
  color: #102a56;
  font-size: 24px;
  font-weight: 700;
}

.rr-content > p {
  color: #65748d;
  font-size: 14px;
  line-height: 1.75;
  margin: 0;
}

.rr-criteria {
  margin-top: 14px;
  padding-top: 16px;
  border-top: 1px solid #e8eef8;
}

.rr-criteria-label {
  display: block;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.01em;
  color: #1559e8;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.rr-criteria ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rr-criteria li {
  position: relative;
  padding-left: 14px;
  font-size: 13px;
  color: #4b6380;
  line-height: 1.5;
}

.rr-criteria li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 7px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #1559e8;
}

/* ── 홈 푸터 ── */
.home-footer {
  background: #0d1117;
  border-radius: 28px 28px 0 0;
  margin-top: 80px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 64px clamp(28px, 6vw, 88px) 44px;
  display: flex;
  flex-direction: column;
  gap: 44px;
}

.footer-nav {
  display: flex;
  align-items: center;
  gap: 36px;
  flex-wrap: wrap;
  padding-bottom: 4px;
}

.footer-nav-brand {
  color: #f97316;
  font-size: 16px;
  font-weight: 900;
  letter-spacing: -0.02em;
  margin-right: 8px;
}

.footer-nav-item {
  color: rgba(255, 255, 255, 0.52);
  font-size: 14px;
  font-weight: 600;
  position: relative;
}

.footer-nav-item::before {
  content: '';
  position: absolute;
  left: -18px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.footer-team {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-team-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.ft-label {
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;
  font-weight: 600;
  min-width: 32px;
}

.ft-name {
  color: #fff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.ft-badge {
  background: rgba(21, 89, 232, 0.22);
  color: #7db3ff;
  font-size: 11px;
  font-weight: 800;
  padding: 3px 11px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.ft-sep {
  color: rgba(255, 255, 255, 0.18);
  font-size: 16px;
}

.ft-email {
  color: rgba(255, 255, 255, 0.42);
  font-size: 14px;
  font-weight: 500;
}

.footer-bottom {
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.25);
  font-size: 13px;
  font-weight: 500;
}

/* ── 스크롤 상단 버튼 ── */
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
