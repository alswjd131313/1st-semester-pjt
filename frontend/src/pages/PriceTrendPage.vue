<template>
  <div class="price-trend-page">
    <div class="page-header">
      <button class="back-btn" @click="router.back()">← 뒤로</button>
      <div>
        <h1>단가 추이</h1>
        <p class="page-sub">나라장터 공공 계약 기준 철근 단가 변화를 확인합니다.</p>
      </div>
    </div>

    <!-- 필터 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>KS 등급</label>
        <select v-model="selectedGrade">
          <option value="">전체</option>
          <option v-for="g in ksGrades" :key="g">{{ g }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>직경</label>
        <select v-model="selectedDiameter">
          <option value="">전체</option>
          <option v-for="d in diameters" :key="d">{{ d }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>기간</label>
        <select v-model="period">
          <option value="3m">3개월</option>
          <option value="6m">6개월</option>
          <option value="1y">1년</option>
        </select>
      </div>
    </div>

    <!-- 요약 카드 -->
    <div class="summary-row">
      <div class="summary-card" v-for="s in summaryStats" :key="s.label">
        <span class="s-label">{{ s.label }}</span>
        <strong class="s-value">{{ s.value }}</strong>
        <span class="s-unit">{{ s.unit }}</span>
      </div>
    </div>

    <!-- 차트 영역 -->
    <section class="chart-card">
      <div class="chart-header">
        <h2>월별 평균 단가 추이</h2>
        <span class="chart-unit">단위: 원/톤</span>
      </div>
      <div class="chart-area">
        <div class="chart-y-axis">
          <span v-for="tick in yTicks" :key="tick">{{ tick.toLocaleString() }}</span>
        </div>
        <div class="chart-bars">
          <div
            v-for="(bar, i) in chartData"
            :key="i"
            class="bar-col"
            @mouseenter="hovered = i"
            @mouseleave="hovered = null"
          >
            <div
              class="bar"
              :class="{ 'bar-active': hovered === i }"
              :style="{ height: barHeight(bar.value) }"
            ></div>
            <span class="bar-label">{{ bar.label }}</span>
            <div v-if="hovered === i" class="bar-tooltip">
              {{ Number(bar.value).toLocaleString() }} 원/톤
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 상세 테이블 -->
    <section class="table-card">
      <h2 class="card-title">계약 이력</h2>
      <div class="table-wrap">
        <div class="table-head">
          <span>계약일</span>
          <span>공급사</span>
          <span>규격</span>
          <span>단가 (원/톤)</span>
        </div>
        <div v-for="(row, i) in tableRows" :key="i" class="table-row">
          <span>{{ row.date }}</span>
          <span>{{ row.supplier }}</span>
          <span>{{ row.spec }}</span>
          <span class="price-cell">{{ Number(row.price).toLocaleString() }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const selectedGrade = ref("SD400");
const selectedDiameter = ref("D13");
const period = ref("6m");
const hovered = ref(null);

const ksGrades = ["SD300", "SD400", "SD500", "SD600"];
const diameters = ["D10", "D13", "D16", "D19", "D22", "D25"];

const BASE_PRICES = {
  SD300: 680000, SD400: 735000, SD500: 875000, SD600: 1045000,
};

const monthLabels = {
  "3m": ["4월", "5월", "6월"],
  "6m": ["1월", "2월", "3월", "4월", "5월", "6월"],
  "1y": ["7월", "8월", "9월", "10월", "11월", "12월", "1월", "2월", "3월", "4월", "5월", "6월"],
};

const chartData = computed(() => {
  const base = BASE_PRICES[selectedGrade.value] ?? 750000;
  const labels = monthLabels[period.value];
  return labels.map((label, i) => ({
    label,
    value: Math.round(base * (0.96 + Math.sin(i * 0.7) * 0.04 + i * 0.002)),
  }));
});

const maxVal = computed(() => Math.max(...chartData.value.map((d) => d.value)));
const minVal = computed(() => Math.min(...chartData.value.map((d) => d.value)));

const yTicks = computed(() => {
  const step = Math.round((maxVal.value - minVal.value) / 4 / 10000) * 10000 || 10000;
  const base = Math.floor(minVal.value / step) * step;
  return [base, base + step, base + step * 2, base + step * 3, base + step * 4].reverse();
});

function barHeight(val) {
  const range = maxVal.value - minVal.value || 1;
  return Math.max(20, ((val - minVal.value) / range) * 200 + 20) + "px";
}

const summaryStats = computed(() => {
  const values = chartData.value.map((d) => d.value);
  const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
  const last = values[values.length - 1];
  const prev = values[values.length - 2] ?? last;
  const diff = ((last - prev) / prev * 100).toFixed(1);
  return [
    { label: "최근 단가", value: last.toLocaleString(), unit: "원/톤" },
    { label: "기간 평균", value: avg.toLocaleString(), unit: "원/톤" },
    { label: "전월 대비", value: diff > 0 ? `+${diff}%` : `${diff}%`, unit: "" },
    { label: "최고 단가", value: maxVal.value.toLocaleString(), unit: "원/톤" },
  ];
});

const SUPPLIERS = ["현대제철", "동국제강", "한국철강", "대한제강", "환영철강"];
const tableRows = computed(() => {
  const base = BASE_PRICES[selectedGrade.value] ?? 750000;
  return Array.from({ length: 12 }, (_, i) => ({
    date: `2025.${String(12 - (i % 6)).padStart(2, "0")}.${String((i % 28) + 1).padStart(2, "0")}`,
    supplier: SUPPLIERS[i % SUPPLIERS.length],
    spec: `${selectedGrade.value} ${selectedDiameter.value}`,
    price: Math.round(base * (0.94 + (i % 5) * 0.025)),
  }));
});
</script>

<style scoped>
.price-trend-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 36px;
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

.page-header h1 { font-size: 28px; font-weight: 700; color: #102a56; margin: 0 0 4px; }
.page-sub { color: #71809a; font-size: 15px; margin: 0; }

.filter-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-group label { font-size: 12px; font-weight: 600; color: #71809a; }
.filter-group select {
  border: 1px solid #dde7f7;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  color: #102a56;
  outline: none;
}
.filter-group select:focus { border-color: #1559e8; }

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.summary-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.s-label { font-size: 13px; color: #71809a; }
.s-value { font-size: 24px; font-weight: 800; color: #102a56; }
.s-unit { font-size: 12px; color: #aab4c4; }

.chart-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.chart-header h2 { font-size: 17px; font-weight: 700; color: #102a56; margin: 0; }
.chart-unit { font-size: 13px; color: #aab4c4; }

.chart-area { display: flex; gap: 12px; align-items: flex-end; height: 260px; }

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 220px;
  text-align: right;
  padding-bottom: 24px;
  flex-shrink: 0;
}
.chart-y-axis span { font-size: 12px; color: #aab4c4; }

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 220px;
  border-bottom: 1px solid #f0f4fa;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  gap: 6px;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, #1559e8, #7ab3ff);
  border-radius: 4px 4px 0 0;
  transition: height 0.4s, opacity 0.15s;
}
.bar.bar-active { opacity: 0.8; }

.bar-label { font-size: 11px; color: #aab4c4; white-space: nowrap; }

.bar-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #102a56;
  color: #fff;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 8px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
}

.table-card {
  background: #fff;
  border: 1px solid #dde7f7;
  border-radius: 16px;
  padding: 28px;
}
.card-title { font-size: 17px; font-weight: 700; color: #102a56; margin: 0 0 20px; }

.table-wrap { overflow-x: auto; }

.table-head {
  display: grid;
  grid-template-columns: 1.2fr 2fr 1.5fr 1.5fr;
  padding: 10px 16px;
  background: #f6f8fc;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #71809a;
  margin-bottom: 4px;
}

.table-row {
  display: grid;
  grid-template-columns: 1.2fr 2fr 1.5fr 1.5fr;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f4fa;
  font-size: 14px;
  color: #4b6380;
}
.price-cell { font-weight: 600; color: #1559e8; }
</style>
