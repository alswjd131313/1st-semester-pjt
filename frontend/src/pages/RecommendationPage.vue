<template>
  <section class="page">
    <div class="page-title">
      <p>Recommendations</p>
      <h1>대체 자재 추천 결과</h1>
      <span>문의 우선순위가 높은 공급사 후보를 카드 형태로 확인하세요.</span>
    </div>

    <RequestSummary :request="request" />

    <p class="notice-box">
      본 추천 결과는 자재 규격, 가격, 거리, 과거 납품 이력을 기반으로 산출됩니다.
      실제 재고 보유 여부와 납품 가능 여부는 공급사에 직접 문의해야 합니다.
    </p>

    <div class="recommendation-list">
      <RecommendationCard v-for="result in results" :key="result.rank" :result="result" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import RequestSummary from "../components/RequestSummary.vue";
import RecommendationCard from "../components/RecommendationCard.vue";
import { getRecommendations } from "../api/materialApi";
import { latestRequest, recommendationResults } from "../data/dummyData";

const route = useRoute();
const request = ref(latestRequest);
const results = ref(recommendationResults);

onMounted(async () => {
  const data = await getRecommendations(route.query.requestId || latestRequest.id);
  request.value = data.request;
  results.value = data.results;
});
</script>
