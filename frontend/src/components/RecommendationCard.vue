<template>
  <article class="recommendation-card">
    <div class="rank-badge">{{ result.rank }}</div>
    <div class="recommendation-main">
      <div class="recommendation-top">
        <div>
          <h3>{{ result.supplierName }}</h3>
          <p>{{ result.materialName }} · {{ result.standard }}</p>
        </div>
        <strong class="score">{{ result.totalScore }}점</strong>
      </div>

      <div class="spec-grid">
        <div><span>최근 단가</span><b>{{ result.price }}</b></div>
        <div><span>거리</span><b>{{ result.distanceKm }}km</b></div>
        <div><span>납품 횟수</span><b>{{ result.deliveryCount }}회</b></div>
        <div><span>감리 승인</span><b :class="{ danger: result.approvalRequired }">{{ result.approvalRequired ? "필요" : "불필요" }}</b></div>
      </div>

      <div class="score-grid">
        <span>가격 {{ result.priceScore }}</span>
        <span>거리 {{ result.distanceScore }}</span>
        <span>신뢰도 {{ result.reliabilityScore }}</span>
      </div>

      <p class="reason">{{ result.reason }}</p>

      <div class="card-actions">
        <button class="btn outline" type="button">상세 보기</button>
        <button class="btn primary" type="button">문의하기</button>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true,
  },
});
</script>
