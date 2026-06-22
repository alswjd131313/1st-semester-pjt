<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getStandardEvidenceForMaterial } from '../data/standardEvidenceData'

const props = defineProps({
  material: { type: String, default: '' },
  category: { type: String, default: '' },
  limit: { type: Number, default: 3 },
})

const route = useRoute()
const searchText = computed(() => [
  props.material,
  props.category,
  route.query.keyword,
  route.query.material,
  route.query.q,
].filter(Boolean).join(' '))

const evidenceItems = computed(() => getStandardEvidenceForMaterial(searchText.value, props.limit))
</script>

<template>
  <section class="standard-evidence-panel">
    <div class="evidence-heading">
      <p>KS 기준</p>
      <h2>대체 가능성 핵심 검토 항목</h2>
    </div>

    <div class="evidence-grid">
      <article v-for="item in evidenceItems" :key="item.id" class="evidence-card">
        <div class="evidence-card__top">
          <span>{{ item.category }}</span>
          <strong>{{ item.standard }}</strong>
        </div>
        <h3>{{ item.title }}</h3>
        <div class="evidence-chip-row">
          <span v-for="metric in item.metrics.slice(0, 3)" :key="metric">{{ metric }}</span>
        </div>
        <p>{{ item.filters[0] }}</p>
        <small>{{ item.approvalRisk }}</small>
      </article>
    </div>
  </section>
</template>

<style scoped>
.standard-evidence-panel {
  margin: 32px 0;
  padding: 28px;
  border: 1px solid rgba(30, 92, 210, 0.14);
  border-radius: 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f4f8ff 100%);
  box-shadow: 0 18px 45px rgba(30, 75, 160, 0.08);
}

.evidence-heading {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.evidence-heading p {
  margin: 0;
  color: #2563eb;
  font-weight: 800;
}

.evidence-heading h2 {
  margin: 0;
  color: #112653;
  font-size: clamp(24px, 3vw, 36px);
  line-height: 1.2;
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.evidence-card {
  display: flex;
  min-height: 100%;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border: 1px solid rgba(30, 92, 210, 0.12);
  border-radius: 22px;
  background: #fff;
}

.evidence-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.evidence-card__top span,
.evidence-chip-row span {
  border-radius: 999px;
  background: #eef5ff;
  color: #1d5ee6;
  font-weight: 800;
}

.evidence-card__top span {
  padding: 7px 11px;
}

.evidence-card__top strong {
  color: #6a7890;
  font-size: 14px;
}

.evidence-card h3 {
  margin: 0;
  color: #122a58;
  font-size: 20px;
  line-height: 1.35;
}

.evidence-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.evidence-chip-row span {
  padding: 6px 10px;
  font-size: 13px;
}

.evidence-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
  color: #52627a;
  line-height: 1.55;
}

.evidence-card p {
  margin: 0;
  color: #465b78;
  font-weight: 800;
  line-height: 1.55;
}

.evidence-card small {
  color: #8a5a10;
  font-weight: 800;
  line-height: 1.45;
}

@media (max-width: 980px) {
  .evidence-grid {
    grid-template-columns: 1fr;
  }
}
</style>
