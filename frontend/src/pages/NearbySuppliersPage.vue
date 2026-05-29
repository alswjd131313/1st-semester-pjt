<template>
  <section class="page">
    <div class="page-title">
      <p>Nearby Suppliers</p>
      <h1>내 주변 공급사</h1>
      <span>{{ currentLocation }}으로 가까운 공급사를 확인합니다. 실제 GPS와 지도 API는 추후 연동 예정입니다.</span>
    </div>

    <section class="nearby-layout">
      <div class="map-card">
        <div class="mock-map">
          <div class="map-grid"></div>
          <div class="site-dot">
            <strong>현장 위치</strong>
            <span>성수동</span>
          </div>
          <button
            v-for="supplier in suppliers"
            :key="supplier.id"
            class="supplier-pin"
            :style="{ left: supplier.x + '%', top: supplier.y + '%' }"
            type="button"
            @click="selectedSupplier = supplier"
          >
            {{ supplier.name }}
            <small>{{ supplier.distanceKm }}km</small>
          </button>
        </div>
        <div class="map-summary">
          <div><span>인근 공급사</span><strong>{{ totalCount }}곳</strong></div>
          <div><span>가장 가까운 거리</span><strong>{{ nearestDistance }}km</strong></div>
          <div><span>기준 위치</span><strong>{{ currentLocation }}</strong></div>
        </div>
      </div>

      <aside class="nearby-list">
        <article
          v-for="supplier in suppliers"
          :key="supplier.id"
          class="nearby-card"
          :class="{ selected: selectedSupplier?.id === supplier.id }"
          @click="selectedSupplier = supplier"
        >
          <div>
            <h2>{{ supplier.name }}</h2>
            <p>{{ supplier.address }}</p>
          </div>
          <strong>{{ supplier.distanceKm }}km</strong>
          <dl>
            <div><dt>납품 이력</dt><dd>{{ supplier.deliveryCount }}회</dd></div>
            <div><dt>연락처</dt><dd>{{ supplier.phone }}</dd></div>
          </dl>
          <p class="material-tags">
            <span v-for="item in supplier.mainMaterials" :key="item">{{ item }}</span>
          </p>
        </article>

        <div class="nearby-actions">
          <RouterLink class="btn outline" to="/">메인으로</RouterLink>
          <RouterLink class="btn primary" :to="{ path: '/request', query: { keyword: '철근 SD400 D10' } }">
            이 위치 기준으로 자재 찾기
          </RouterLink>
        </div>
      </aside>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { getNearbySuppliers } from "../api/materialApi";

const currentLocation = ref("서울 성수동 기준");
const totalCount = ref(0);
const suppliers = ref([]);
const selectedSupplier = ref(null);
const nearestDistance = computed(() => {
  if (!suppliers.value.length) return "-";
  return Math.min(...suppliers.value.map((supplier) => supplier.distanceKm));
});

onMounted(async () => {
  const data = await getNearbySuppliers();
  currentLocation.value = data.currentLocation;
  totalCount.value = data.totalCount;
  suppliers.value = data.suppliers;
  selectedSupplier.value = data.suppliers[0];
});
</script>
