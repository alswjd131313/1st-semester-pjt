<template>
  <section class="kakao-map-panel">
    <div class="section-title-row">
      <div>
        <h2>현장과 추천 공급사 위치</h2>
        <p>선택한 현장 주소와 추천 공급사의 등록 좌표를 표시합니다.</p>
      </div>
      <span>{{ validSuppliers.length }}개 공급사</span>
    </div>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <div ref="mapElement" class="kakao-map-canvas" aria-label="추천 공급사 카카오맵"></div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";

const props = defineProps({
  site: { type: Object, default: () => ({}) },
  suppliers: { type: Array, default: () => [] },
});

const mapElement = ref(null);
const errorMessage = ref("");
const validSuppliers = computed(() =>
  props.suppliers.filter((supplier) => Number.isFinite(Number(supplier.latitude)) && Number.isFinite(Number(supplier.longitude))),
);

onMounted(renderMap);
watch(() => [props.site, props.suppliers], renderMap, { deep: true });

async function renderMap() {
  await nextTick();
  try {
    await loadKakaoMapSdk();
    const kakao = window.kakao;
    const siteLat = Number(props.site.latitude);
    const siteLng = Number(props.site.longitude);
    if (!Number.isFinite(siteLat) || !Number.isFinite(siteLng)) {
      errorMessage.value = "현장 좌표가 없어 지도를 표시할 수 없습니다.";
      return;
    }

    errorMessage.value = "";
    const sitePosition = new kakao.maps.LatLng(siteLat, siteLng);
    const map = new kakao.maps.Map(mapElement.value, { center: sitePosition, level: 7 });
    const bounds = new kakao.maps.LatLngBounds();
    addMarker(kakao, map, sitePosition, `현장 · ${props.site.address || "선택 주소"}`);
    bounds.extend(sitePosition);

    validSuppliers.value.forEach((supplier) => {
      const position = new kakao.maps.LatLng(Number(supplier.latitude), Number(supplier.longitude));
      addMarker(kakao, map, position, `${supplier.supplierName} · ${supplier.distanceKm}km`);
      bounds.extend(position);
    });

    if (validSuppliers.value.length) {
      map.setBounds(bounds);
    }
  } catch (error) {
    errorMessage.value = error.message || "카카오맵을 불러오지 못했습니다.";
  }
}

function addMarker(kakao, map, position, text) {
  const marker = new kakao.maps.Marker({ map, position });
  const infoWindow = new kakao.maps.InfoWindow({
    content: `<div class="map-info-window">${text}</div>`,
  });
  kakao.maps.event.addListener(marker, "click", () => infoWindow.open(map, marker));
}

function loadKakaoMapSdk() {
  if (window.kakao?.maps?.Map) {
    return Promise.resolve();
  }
  if (window.kakao?.maps?.load) {
    return new Promise((resolve) => window.kakao.maps.load(resolve));
  }

  const key = import.meta.env.VITE_KAKAO_JAVASCRIPT_KEY;
  if (!key) {
    return Promise.reject(new Error("카카오 JavaScript 키가 설정되지 않았습니다."));
  }

  return new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-kakao-map-sdk="true"]');
    if (existing) {
      existing.addEventListener("load", () => window.kakao.maps.load(resolve), { once: true });
      existing.addEventListener("error", () => reject(new Error("카카오맵 SDK 로드에 실패했습니다.")), { once: true });
      return;
    }

    const script = document.createElement("script");
    script.dataset.kakaoMapSdk = "true";
    script.async = true;
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${encodeURIComponent(key)}&autoload=false&libraries=services`;
    script.onload = () => window.kakao.maps.load(resolve);
    script.onerror = () => reject(new Error("카카오맵 SDK 로드에 실패했습니다."));
    document.head.appendChild(script);
  });
}
</script>
