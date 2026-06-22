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
  <section class="sep">
    <div class="sep-heading">
      <p class="sep-eyebrow">KS 기준</p>
      <h2>대체 가능성 핵심 검토 항목</h2>
    </div>

    <div class="sep-grid">
      <article v-for="item in evidenceItems" :key="item.id" class="sep-card">
        <div class="sep-card-header">
          <strong class="sep-category">{{ item.category }}</strong>
          <span class="sep-ks-badge">{{ item.standard }}</span>
        </div>

        <div class="sep-chips">
          <span v-for="metric in item.metrics.slice(0, 3)" :key="metric" class="sep-chip">
            {{ metric }}
          </span>
        </div>

        <p class="sep-filter">{{ item.filters[0] }}</p>

        <p class="sep-risk">⚠ {{ item.approvalRisk.split('，')[0].split(',')[0].trim() }}</p>
      </article>
    </div>

    <p class="sep-note">KS 규격을 통과한 자재만 대체 후보로 추천됩니다.</p>
  </section>
</template>

<style scoped>
.sep {
  margin: 40px 0;
  padding: 32px 32px 24px;
  border: 1px solid rgba(30, 92, 210, 0.12);
  border-radius: 28px;
  background: linear-gradient(135deg, #fff 0%, #f4f8ff 100%);
  box-shadow: 0 12px 40px rgba(30, 75, 160, 0.07);
}

.sep-heading {
  margin-bottom: 24px;
}

.sep-eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.sep-heading h2 {
  margin: 0;
  color: #112653;
  font-size: clamp(20px, 2.4vw, 28px);
  font-weight: 700;
  line-height: 1.2;
}

.sep-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.sep-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 18px 16px;
  border: 1px solid rgba(30, 92, 210, 0.11);
  border-radius: 18px;
  background: #fff;
}

.sep-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.sep-category {
  font-size: 18px;
  font-weight: 800;
  color: #112653;
}

.sep-ks-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #1559e8;
  background: #eef5ff;
  border: 1px solid #c8d8f2;
}

.sep-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sep-chip {
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  background: #f2f5fa;
  border: 1px solid #e2eaf5;
}

.sep-filter {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #1e4fc2;
  line-height: 1.5;
  padding: 10px 12px;
  background: #eef5ff;
  border-radius: 10px;
}

.sep-risk {
  margin: 0;
  font-size: 12px;
  color: #92600a;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 7px 11px;
  line-height: 1.5;
}

.sep-note {
  margin: 0;
  font-size: 13px;
  color: #71809a;
  text-align: center;
}

@media (max-width: 860px) {
  .sep-grid {
    grid-template-columns: 1fr;
  }

  .sep {
    padding: 24px 20px;
  }
}
</style>
