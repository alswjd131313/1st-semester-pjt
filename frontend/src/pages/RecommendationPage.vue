<template>
  <section class="page-wrap">
    <div class="page-heading">
      <p class="eyebrow">Step 2</p>
      <h1>추천 결과</h1>
      <p>
        본 추천 결과는 자재 규격, 가격, 거리, 과거 납품 이력을 기반으로 산출됩니다.
        실제 재고와 납품 가능 여부는 공급사에 직접 문의해야 합니다.
      </p>
    </div>

    <div v-if="request" class="summary-card">
      <strong>{{ request.materialName }} {{ request.strengthGrade }}</strong>
      <span>현장 위치: {{ request.siteAddress || "미입력" }}</span>
      <span>필요 수량: {{ request.requiredQuantity || "미입력" }}</span>
      <span>{{ request.isUrgent ? "긴급 요청" : "일반 요청" }}</span>
    </div>

    <div class="recommendation-grid">
      <article v-for="item in recommendations" :key="item.rank" class="recommendation-card">
        <div class="card-topline">
          <span class="rank-badge">{{ item.rank }}순위</span>
          <span v-if="item.isRegisteredSupplier" class="source-badge">등록 공급사</span>
          <span :class="['approval-badge', { warn: item.approvalRequired }]">
            {{ item.approvalRequired ? "감리 승인 필요" : "승인 리스크 낮음" }}
          </span>
        </div>

        <h2>{{ item.supplierName }}</h2>
        <p class="material-line">{{ item.materialName }} · {{ item.standard }}</p>

        <dl class="score-list">
          <div>
            <dt>최근 단가</dt>
            <dd>{{ item.price }}</dd>
          </div>
          <div>
            <dt>거리</dt>
            <dd>{{ item.distanceKm }}km</dd>
          </div>
          <div>
            <dt>납품 이력</dt>
            <dd>{{ item.deliveryCount }}회</dd>
          </div>
          <div>
            <dt>최종 점수</dt>
            <dd>{{ item.totalScore }}점</dd>
          </div>
        </dl>

        <div v-if="item.contact || item.serviceArea" class="supplier-meta">
          <span v-if="item.contact">연락처 {{ item.contact }}</span>
          <span v-if="item.serviceArea">납품 가능 {{ item.serviceArea }}</span>
        </div>

        <div class="score-bars">
          <span>가격 {{ item.priceScore }}</span>
          <span>거리 {{ item.distanceScore }}</span>
          <span>신뢰도 {{ item.reliabilityScore }}</span>
        </div>

        <p class="reason">{{ item.reason }}</p>

        <div class="card-actions">
          <button type="button" class="secondary-button">상세 보기</button>
          <button type="button" class="primary-button">문의하기</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getLatestMaterialRequest, getRecommendations } from "../api/materialApi";

const route = useRoute();
const request = ref(null);
const recommendations = ref([]);

onMounted(async () => {
  request.value = await getLatestMaterialRequest();
  recommendations.value = await getRecommendations(route.query.requestId);
});
</script>
