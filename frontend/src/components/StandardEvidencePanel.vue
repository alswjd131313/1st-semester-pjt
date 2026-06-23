<template>
  <section class="sep">
    <div class="sep-aside">
      <h2>대체 후보는<br>이렇게 검토합니다</h2>
      <p>PaceFlow는 다각도의 기준으로 대체 가능성을 검토하여 안전하고 신뢰할 수 있는 자재만 추천합니다.</p>
      <div class="sep-arrows">
        <button class="sep-arrow" @click="prev" aria-label="이전">←</button>
        <span class="sep-count">{{ String(activeIdx + 1).padStart(2, '0') }} / 04</span>
        <button class="sep-arrow" @click="next" aria-label="다음">→</button>
      </div>
    </div>

    <div class="sep-stage" ref="stageRef">
      <div class="sep-track" :style="trackStyle">
        <article
          v-for="(card, i) in CARDS"
          :key="card.id"
          :class="['sep-card', cardClass(i)]"
        >
          <div class="sep-card-header">
            <span class="sep-icon-wrap" :style="{ background: card.iconBg }">
              <span class="sep-icon-emoji">{{ card.icon }}</span>
            </span>
            <span class="sep-num" :style="{ color: card.color }">{{ card.num }}</span>
          </div>

          <h3 class="sep-title">{{ card.title }}</h3>
          <div class="sep-divider"></div>

          <ul class="sep-list">
            <li v-for="item in card.items" :key="item">{{ item }}</li>
          </ul>

          <div class="sep-summary" :style="{ background: card.summaryBg, color: card.color }">
            <span class="sep-check">✓</span>
            {{ card.summary }}
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

defineProps({
  material: { type: String, default: '' },
  category: { type: String, default: '' },
  limit: { type: Number, default: 3 },
})

const CARDS = [
  {
    id: 1, num: '01', icon: '🛡️', title: '물성 기준 검토',
    color: '#1559e8', iconBg: '#eef5ff', summaryBg: '#eef5ff',
    items: ['항복강도', '인장강도', '연신율', '탄소당량 (Ceq)'],
    summary: '구조 성능에 직접 영향을 미치는 핵심 물성을 검토합니다.',
  },
  {
    id: 2, num: '02', icon: '📋', title: '규격 적합성 검토',
    color: '#059669', iconBg: '#ecfdf5', summaryBg: '#ecfdf5',
    items: ['KS 등급 및 규격', '강종 및 재질', '규격 코드 확인', 'ASTM / JIS 등 국제 규격 대용 여부'],
    summary: 'KS 규격과 호환되는지 면밀히 검토합니다.',
  },
  {
    id: 3, num: '03', icon: '📍', title: '공급 가능성 검토',
    color: '#7c3aed', iconBg: '#f5f3ff', summaryBg: '#f5f3ff',
    items: ['현장까지의 거리', '납품 이력 및 실적', '최근 단가 수준', '등록 공급사 여부'],
    summary: '안정적인 납품과 경쟁력 있는 조건을 갖춘 공급사만 선발합니다.',
  },
  {
    id: 4, num: '04', icon: '⚠️', title: '승인 리스크 검토',
    color: '#d97706', iconBg: '#fffbeb', summaryBg: '#fffbeb',
    items: ['국제 규격 사용 여부', '강도 상향 여부', '규격/치수 변경 여부', '주조 검토 필요 여부'],
    summary: '승인 지연 또는 추가 검토가 필요한 리스크를 사전에 안내합니다.',
  },
]

const stageRef = ref(null)
const stageW = ref(700)
const activeIdx = ref(0)
let ro = null

onMounted(() => {
  if (!stageRef.value) return
  stageW.value = stageRef.value.clientWidth
  ro = new ResizeObserver(([e]) => { stageW.value = e.contentRect.width })
  ro.observe(stageRef.value)
})

onUnmounted(() => ro?.disconnect())

const CARD_RATIO = 0.74
const GAP = 20

const cardW = computed(() => stageW.value * CARD_RATIO)

const trackStyle = computed(() => {
  const offset = activeIdx.value * (cardW.value + GAP) - (stageW.value - cardW.value) / 2
  return { transform: `translateX(${-offset}px)` }
})

function cardClass(i) {
  const diff = i - activeIdx.value
  if (diff === 0) return 'is-active'
  if (Math.abs(diff) === 1) return 'is-adj'
  return 'is-far'
}

function prev() { activeIdx.value = (activeIdx.value - 1 + CARDS.length) % CARDS.length }
function next() { activeIdx.value = (activeIdx.value + 1) % CARDS.length }
</script>

<style scoped>
.sep {
  display: grid;
  grid-template-columns: minmax(240px, 320px) minmax(0, 1fr);
  gap: 48px;
  align-items: center;
  padding: 64px 0;
}

.sep-aside {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sep-aside h2 {
  margin: 0;
  color: #102a56;
  font-size: clamp(28px, 3.2vw, 42px);
  font-weight: 800;
  line-height: 1.25;
}

.sep-aside p {
  margin: 0;
  color: #65748d;
  font-size: 15px;
  line-height: 1.7;
}

.sep-arrows {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.sep-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: 1px solid #c8d8f2;
  border-radius: 50%;
  background: #fff;
  color: #1559e8;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.sep-arrow:hover {
  background: #eef5ff;
  border-color: #1559e8;
}

.sep-count {
  font-size: 15px;
  font-weight: 800;
  color: #8fa3be;
}

.sep-stage {
  overflow: hidden;
  padding: 24px 0;
}

.sep-track {
  display: flex;
  gap: 20px;
  transition: transform 0.42s cubic-bezier(0.32, 0.96, 0.58, 1);
}

.sep-card {
  flex: 0 0 74%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 28px 26px 24px;
  border: 1px solid #dbe6f8;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 8px 32px rgba(31, 61, 115, 0.07);
  transition: transform 0.42s cubic-bezier(0.32, 0.96, 0.58, 1), opacity 0.42s;
  transform-origin: center center;
}

.sep-card.is-active {
  transform: scale(1);
  opacity: 1;
  box-shadow: 0 20px 60px rgba(31, 61, 115, 0.14);
}

.sep-card.is-adj {
  transform: scale(0.91);
  opacity: 0.68;
}

.sep-card.is-far {
  transform: scale(0.83);
  opacity: 0.4;
}

.sep-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.sep-icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
}

.sep-icon-emoji {
  font-size: 24px;
}

.sep-num {
  font-size: 28px;
  font-weight: 900;
  line-height: 1;
}

.sep-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #102a56;
  line-height: 1.3;
}

.sep-divider {
  height: 1px;
  background: #eef2f8;
}

.sep-list {
  margin: 0;
  padding: 0 0 0 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.sep-list li {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  line-height: 1.5;
}

.sep-summary {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.55;
}

.sep-check {
  font-size: 15px;
  font-weight: 900;
  flex-shrink: 0;
  margin-top: 1px;
}

@media (max-width: 820px) {
  .sep {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .sep-aside h2 br { display: none; }
}
</style>
