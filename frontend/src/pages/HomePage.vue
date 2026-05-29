<template>
  <section class="hero-section">
    <div class="hero-content">
      <p class="eyebrow">Keep Your Supply Moving</p>
      <h1>공사 지연은 막고,<br />대체 자재는 빠르게 찾으세요</h1>
      <p class="hero-copy">
        부족하거나 대체가 필요한 자재를 입력하면 문의 우선순위가 높은 공급사 후보를 빠르게 확인할 수 있습니다.
      </p>
      <SearchBar placeholder="예: 철근 SD400 D10, H빔 300x300, 시멘트 1종" @submit="handleSearch" />
      <CategoryTabs :categories="categories" @select="handleCategory" />
    </div>
    <aside class="hero-dashboard">
      <button class="mini-card highlight mini-card-action" type="button" @click="findNearbySuppliers">
        <span>내 주변 공급사</span>
        <strong>12곳</strong>
        <p>지도에서 가까운 공급사 보기</p>
      </button>
      <div class="mini-card">
        <span>가장 가까운 거리</span>
        <strong>3.2km</strong>
      </div>
      <div class="mini-card">
        <span>납품 이력</span>
        <strong>42회</strong>
      </div>
      <div class="mini-card wide">
        <span>주의</span>
        <p>실시간 재고는 보장하지 않으며, 공급사 확인이 필요합니다.</p>
      </div>
    </aside>
  </section>

  <section class="page-grid">
    <MaterialRanking :materials="rankingMaterials" @select="handleRanking" />
    <div class="stack">
      <RecommendationMethodCard />
      <SupplierNoticeBox />
    </div>
  </section>

  <section class="values">
    <ValueCard title="지연 최소화" description="빠른 대체 자재 추천으로 공사 지연을 줄여드립니다." />
    <ValueCard title="신뢰할 수 있는 데이터" description="규격·품질·납품 이력을 기반으로 검증된 공급사만 추천합니다." />
    <ValueCard title="거리·가격 최적화" description="현장 위치와 가격을 고려해 효율적인 공급사를 제안합니다." />
    <ValueCard title="실적 기반 추천" description="과거 납품 이력과 고객 평가를 반영해 우선순위가 높은 공급사를 제공합니다." />
  </section>
</template>

<script setup>
import { useRouter } from "vue-router";
import SearchBar from "../components/SearchBar.vue";
import CategoryTabs from "../components/CategoryTabs.vue";
import MaterialRanking from "../components/MaterialRanking.vue";
import RecommendationMethodCard from "../components/RecommendationMethodCard.vue";
import SupplierNoticeBox from "../components/SupplierNoticeBox.vue";
import ValueCard from "../components/ValueCard.vue";
import { categories, rankingMaterials } from "../data/dummyData";

const router = useRouter();

function moveToRequest(keyword = "") {
  router.push({ path: "/request", query: keyword ? { keyword } : {} });
}

function handleSearch(keyword) {
  moveToRequest(keyword);
}

function handleCategory(category) {
  const examples = {
    철근: "철근 SD400 D10",
    시멘트: "시멘트 1종",
    H빔: "H빔 300x300",
    전선관: "전선관 25A",
    단열재: "단열재 50T",
  };
  moveToRequest(examples[category.name]);
}

function handleRanking(item) {
  moveToRequest(item.name);
}

function findNearbySuppliers() {
  router.push("/nearby-suppliers");
}
</script>
