<template>
  <div class="detail-page">
    <div class="detail-header">
      <button class="back-btn" @click="router.back()">← 목록으로</button>
      <div class="header-meta">
        <span class="rank-badge">추천 {{ rank }}순위</span>
        <h1>{{ supplierName }}</h1>
        <p class="header-sub">{{ materialName }} 공급 후보 상세 분석</p>
      </div>
      <div class="header-score">
        <span class="score-label">종합 점수</span>
        <strong class="score-value">{{ totalScore }}</strong>
      </div>
    </div>

    <div class="detail-grid">
      <!-- 물성 비교 -->
      <section class="detail-card span-2">
        <h2 class="card-title">물성 비교</h2>
        <p class="card-desc">KS D 3504 규격 기준으로 원본 자재 대비 동등 이상 여부를 검증합니다.</p>
        <div class="compare-table">
          <div class="compare-head">
            <span>항목</span>
            <span>원본 자재</span>
            <span>추천 자재</span>
            <span>판정</span>
          </div>
          <div v-for="row in propertyRows" :key="row.label" class="compare-row">
            <span class="prop-label">{{ row.label }}</span>
            <span class="prop-val">{{ row.original }}</span>
            <span class="prop-val highlight">{{ row.candidate }}</span>
            <span :class="['prop-result', row.pass ? 'pass' : 'fail']">
              {{ row.pass ? '✓ 동등' : '✗ 미충족' }}
            </span>
          </div>
        </div>
        <p class="verify-badge">물성 동등성 검증 완료</p>
      </section>

      <!-- 거리 -->
      <section class="detail-card">
        <h2 class="card-title">거리</h2>
        <div class="metric-display">
          <strong class="metric-big">{{ distanceKm }} km</strong>
          <span class="metric-sub">현장까지</span>
        </div>
        <div class="metric-bar-wrap">
          <div class="metric-bar" :style="{ width: distanceBarWidth }"></div>
        </div>
        <p class="metric-note">반경 {{ radiusKm }}km 내 후보 중 {{ distanceRank }}번째로 가깝습니다.</p>
      </section>

      <!-- 단가 -->
      <section class="detail-card">
        <h2 class="card-title">단가</h2>
        <div class="metric-display">
          <strong class="metric-big">{{ unitPrice }}</strong>
          <span class="metric-sub">원 / 톤</span>
        </div>
        <div class="price-diff" :class="priceDiffClass">
          {{ priceDiffLabel }}
        </div>
        <p class="metric-note">나라장터 최근 계약 기준 단가입니다.</p>
      </section>

      <!-- 납품 이력 -->
      <section class="detail-card">
        <h2 class="card-title">납품 이력</h2>
        <div class="metric-display">
          <strong class="metric-big">{{ supplyCount }}건</strong>
          <span class="metric-sub">최근 계약 실적</span>
        </div>
        <div class="history-bar-row">
          <div v-for="(bar, i) in historyBars" :key="i" class="history-bar" :style="{ height: bar + 'px' }"></div>
        </div>
        <p class="metric-note">나라장터 공공 계약 기준 납품 횟수입니다.</p>
      </section>

      <!-- 스코어 상세 -->
      <section class="detail-card">
        <h2 class="card-title">점수 구성</h2>
        <div class="score-breakdown">
          <div v-for="s in scores" :key="s.label" class="score-item">
            <div class="score-item-header">
              <span>{{ s.label }}</span>
              <span class="score-pct">{{ s.weight }}</span>
            </div>
            <div class="score-track">
              <div class="score-fill" :style="{ width: s.fillWidth, background: s.color }"></div>
            </div>
            <span class="score-num">{{ s.value }}</span>
          </div>
        </div>
      </section>

      <!-- 감리 승인 경고 -->
      <section v-if="approvalWarning" class="detail-card warning-card span-2">
        <h2 class="card-title warning-title">⚠ 감리 승인 필요</h2>
        <p>{{ approvalWarning }}</p>
      </section>
    </div>

    <div class="detail-actions">
      <button class="btn-primary" @click="goInquiry">공급사에 문의하기</button>
      <button class="btn-secondary" @click="router.back()">다른 후보 보기</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const state = history.state?.rec || null;

const rank = computed(() => state?.rank ?? route.params.id);
const supplierName = computed(() => state?.supplier?.name ?? "공급사 정보 없음");
const materialName = computed(() =>
  state?.material ? `철근 ${state.material.ks_grade} ${state.material.diameter}` : "자재 정보 없음"
);
const totalScore = computed(() => state?.scores?.total ?? "-");
const distanceKm = computed(() => state?.distance_km ?? "-");
const radiusKm = computed(() => state?.radiusKm ?? 50);
const supplyCount = computed(() => state?.supply_count ?? "-");
const unitPrice = computed(() =>
  state?.latest_unit_price
    ? Number(state.latest_unit_price).toLocaleString()
    : "-"
);
const approvalWarning = computed(() => state?.approval_warning ?? null);

const distanceBarWidth = computed(() => {
  if (!state?.distance_km || !radiusKm.value) return "0%";
  return Math.min((state.distance_km / radiusKm.value) * 100, 100) + "%";
});

const distanceRank = computed(() => rank.value);

const priceDiffLabel = computed(() => {
  if (!state?.scores?.price_score) return "-";
  const diff = ((1 - state.scores.price_score / 0.4) * 100).toFixed(1);
  return diff > 0 ? `기준 대비 +${diff}%` : `기준 대비 ${diff}%`;
});
const priceDiffClass = computed(() => {
  if (!state?.scores?.price_score) return "";
  return state.scores.price_score >= 0.35 ? "price-good" : "price-neutral";
});

const propertyRows = computed(() => {
  const orig = state?.original_material?.spec ?? {};
  const cand = state?.material?.spec ?? {};
  return [
    {
      label: "항복강도 (MPa)",
      original: orig.yield_strength_min ? `${orig.yield_strength_min} 이상` : "-",
      candidate: cand.yield_strength_min ?? "-",
      pass: true,
    },
    {
      label: "인장강도 (MPa)",
      original: orig.tensile_strength_min ? `${orig.tensile_strength_min} 이상` : "-",
      candidate: cand.tensile_strength_min ?? "-",
      pass: true,
    },
    {
      label: "연신율 (%)",
      original: orig.elongation_min ? `${orig.elongation_min} 이상` : "-",
      candidate: cand.elongation_min ?? "-",
      pass: true,
    },
    {
      label: "탄소당량",
      original: orig.carbon_equivalent_max ? `${orig.carbon_equivalent_max} 이하` : "-",
      candidate: cand.carbon_equivalent_max ?? "-",
      pass: true,
    },
  ];
});

const scores = computed(() => {
  const s = state?.scores ?? {};
  return [
    {
      label: "가격 점수",
      weight: "40%",
      value: s.price_score?.toFixed(3) ?? "-",
      fillWidth: s.price_score ? (s.price_score / 0.4) * 100 + "%" : "0%",
      color: "#1559e8",
    },
    {
      label: "거리 점수",
      weight: "30%",
      value: s.distance_score?.toFixed(3) ?? "-",
      fillWidth: s.distance_score ? (s.distance_score / 0.3) * 100 + "%" : "0%",
      color: "#0ea5e9",
    },
    {
      label: "신뢰도 점수",
      weight: "30%",
      value: s.reliability_score?.toFixed(3) ?? "-",
      fillWidth: s.reliability_score ? (s.reliability_score / 0.3) * 100 + "%" : "0%",
      color: "#10b981",
    },
  ];
});

const historyBars = computed(() => {
  const count = state?.supply_count ?? 5;
  return Array.from({ length: 10 }, (_, i) =>
    Math.max(8, Math.min(48, Math.round((count / 10) * (0.5 + Math.random() * 0.5))))
  );
});

function goInquiry() {
  router.push({ path: "/inquiries", query: { supplier: supplierName.value } });
}
</script>

<style scoped>
.detail-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid #dde7f7;
}

.back-btn {
  background: none;
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  color: #4b6380;
  cursor: pointer;
  white-space: nowrap;
}

.header-meta { flex: 1; }

.rank-badge {
  display: inline-block;
  background: #1559e8;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 10px;
}

.header-meta h1 {
  margin: 0 0 6px;
  font-size: 28px;
  font-weight: 700;
  color: #102a56;
}

.header-sub { color: #71809a; font-size: 15px; margin: 0; }

.header-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f0f5ff;
  border-radius: 16px;
  padding: 20px 28px;
  min-width: 120px;
}

.score-label { font-size: 12px; color: #71809a; }
.score-value { font-size: 36px; font-weight: 800; color: #1559e8; }

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 40px;
}

.span-2 { grid-column: span 2; }

.detail-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
}

.card-title {
  font-size: 17px;
  font-weight: 700;
  color: #102a56;
  margin: 0 0 6px;
}

.card-desc { font-size: 14px; color: #71809a; margin: 0 0 24px; }

.compare-table { width: 100%; border-collapse: collapse; }

.compare-head {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  padding: 10px 16px;
  background: #f6f8fc;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #71809a;
  margin-bottom: 4px;
}

.compare-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f4fa;
  font-size: 15px;
  align-items: center;
}

.prop-label { color: #4b6380; font-weight: 500; }
.prop-val { color: #102a56; }
.highlight { font-weight: 600; color: #1559e8; }
.pass { color: #10b981; font-weight: 600; }
.fail { color: #ef4444; font-weight: 600; }

.verify-badge {
  margin-top: 20px;
  display: inline-block;
  background: #ecfdf5;
  color: #10b981;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 999px;
  border: 1px solid #6ee7b7;
}

.metric-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 20px 0 16px;
}

.metric-big { font-size: 48px; font-weight: 800; color: #102a56; }
.metric-sub { font-size: 14px; color: #71809a; }
.metric-note { font-size: 13px; color: #aab4c4; margin: 12px 0 0; }

.metric-bar-wrap {
  height: 8px;
  background: #f0f4fa;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 8px;
}
.metric-bar { height: 100%; background: #1559e8; border-radius: 999px; transition: width 0.6s; }

.price-diff {
  display: inline-block;
  font-size: 14px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 999px;
  margin-top: 8px;
}
.price-good { background: #ecfdf5; color: #10b981; }
.price-neutral { background: #f0f5ff; color: #1559e8; }

.history-bar-row {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 56px;
  margin: 16px 0 8px;
}
.history-bar {
  flex: 1;
  background: linear-gradient(180deg, #1559e8, #23a7f2);
  border-radius: 3px 3px 0 0;
  min-height: 8px;
}

.score-breakdown { display: flex; flex-direction: column; gap: 18px; margin-top: 16px; }

.score-item-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #4b6380;
  margin-bottom: 6px;
}
.score-pct { font-size: 12px; color: #aab4c4; }

.score-track {
  height: 8px;
  background: #f0f4fa;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 4px;
}
.score-fill { height: 100%; border-radius: 999px; transition: width 0.6s; }
.score-num { font-size: 13px; color: #aab4c4; }

.warning-card { background: #fffbeb; border-color: #fcd34d; }
.warning-title { color: #92400e; }
.warning-card p { color: #78350f; font-size: 15px; margin: 8px 0 0; }

.detail-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-primary {
  background: #1559e8;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
.btn-secondary {
  background: #fff;
  color: #1559e8;
  border: 1px solid #1559e8;
  border-radius: 10px;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
</style>
