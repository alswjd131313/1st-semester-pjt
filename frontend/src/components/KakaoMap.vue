<template>
  <section class="kakao-map-panel">
    <div class="section-title-row">
      <div>
        <h2>현장과 추천 공급사 위치</h2>
        <p>공급사 등록 주소와 계약기관 추정 위치를 구분해 표시합니다.</p>
      </div>
      <span>{{ validSuppliers.length }}개 공급사</span>
    </div>
    <div class="map-legend" aria-label="지도 위치 기준">
      <span class="site">현장</span>
      <span class="actual">공급사 위치 {{ actualSupplierCount }}곳</span>
      <span class="estimated">계약기관 추정 {{ estimatedSupplierCount }}곳</span>
    </div>
    <div class="kakao-map-frame">
      <div ref="mapElement" class="kakao-map-canvas" aria-label="추천 공급사 카카오맵"></div>
      <div v-if="errorMessage" class="kakao-map-unavailable" role="status">
        <strong>지도를 표시할 수 없습니다.</strong>
        <span>{{ errorMessage }}</span>
      </div>
    </div>
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
let renderSequence = 0;
const validSuppliers = computed(() =>
  props.suppliers.filter((supplier) => isKoreaMapCoordinate(supplier.latitude, supplier.longitude)),
);
const actualSupplierCount = computed(() =>
  validSuppliers.value.filter((supplier) => supplier.locationBasis === "supplier_address").length,
);
const estimatedSupplierCount = computed(() =>
  validSuppliers.value.filter((supplier) => supplier.locationBasis === "contract_agency_estimated").length,
);

onMounted(renderMap);
watch(() => [props.site, props.suppliers], renderMap, { deep: true });

async function renderMap() {
  const currentRender = ++renderSequence;
  await nextTick();
  try {
    await loadKakaoMapSdk();
    const kakao = window.kakao;
    const siteLat = Number(props.site.latitude);
    const siteLng = Number(props.site.longitude);
    if (!isKoreaMapCoordinate(siteLat, siteLng)) {
      errorMessage.value = "현장 좌표가 없어 지도를 표시할 수 없습니다.";
      return;
    }

    errorMessage.value = "";
    const sitePosition = new kakao.maps.LatLng(siteLat, siteLng);
    const map = new kakao.maps.Map(mapElement.value, { center: sitePosition, level: 7 });
    const bounds = new kakao.maps.LatLngBounds();
    addMarker(kakao, map, sitePosition, `현장 · ${props.site.address || "선택 주소"}`, "site");
    bounds.extend(sitePosition);

    validSuppliers.value.forEach((supplier) => {
      const position = new kakao.maps.LatLng(Number(supplier.latitude), Number(supplier.longitude));
      addMarker(kakao, map, position, getSupplierMarkerText(supplier), getSupplierMarkerVariant(supplier));
      bounds.extend(position);
    });

    if (validSuppliers.value.length) {
      map.setBounds(bounds);
    }

    window.setTimeout(() => detectMapAuthorizationFailure(currentRender), 1800);
  } catch (error) {
    errorMessage.value = error.message || "카카오맵을 불러오지 못했습니다.";
  }
}

function isKoreaMapCoordinate(latitude, longitude) {
  if (latitude === null || latitude === undefined || longitude === null || longitude === undefined) {
    return false;
  }

  const lat = Number(latitude);
  const lng = Number(longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 32 && lat <= 39 && lng >= 124 && lng <= 132;
}

function detectMapAuthorizationFailure(currentRender) {
  if (currentRender !== renderSequence || !mapElement.value) {
    return;
  }

  const images = [...mapElement.value.querySelectorAll("img")];
  const whiteTiles = images.filter((image) => image.src.includes("/dmaps/apis/white.png"));
  const mapTiles = images.filter((image) => image.naturalWidth >= 128 && image.naturalHeight >= 128);

  if (whiteTiles.length >= 4 && mapTiles.length === 0) {
    errorMessage.value = "카카오 JavaScript 키의 웹 플랫폼 도메인 등록을 확인해주세요.";
  }
}

function getSupplierMarkerText(supplier) {
  const distance = Number(supplier.distanceKm);
  if (supplier.locationBasis === "supplier_address" && Number.isFinite(distance)) {
    return `${supplier.supplierName} · 공급사 위치 · ${distance}km`;
  }

  if (supplier.locationBasis === "contract_agency_estimated") {
    return `${supplier.supplierName} · 계약기관 추정 위치`;
  }

  return `${supplier.supplierName} · 좌표 확인`;
}

function getSupplierMarkerVariant(supplier) {
  if (supplier.locationBasis === "supplier_address") {
    return "actual";
  }

  if (supplier.locationBasis === "contract_agency_estimated") {
    return "estimated";
  }

  return "unknown";
}

function addMarker(kakao, map, position, text, variant = "actual") {
  const marker = new kakao.maps.Marker({
    map,
    position,
    image: createMarkerImage(kakao, variant),
  });
  const infoWindow = new kakao.maps.InfoWindow({
    content: `<div class="map-info-window">${text}</div>`,
  });
  kakao.maps.event.addListener(marker, "click", () => infoWindow.open(map, marker));
}

function createMarkerImage(kakao, variant) {
  const colors = {
    site: "#1559e8",
    actual: "#0f766e",
    estimated: "#f97316",
    unknown: "#64748b",
  };
  const color = colors[variant] || colors.unknown;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">
      <path fill="${color}" d="M17 0C7.6 0 0 7.5 0 16.8c0 12.6 17 25.2 17 25.2s17-12.6 17-25.2C34 7.5 26.4 0 17 0z"/>
      <circle cx="17" cy="16.8" r="6.8" fill="#fff"/>
    </svg>
  `.trim();
  const url = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  return new kakao.maps.MarkerImage(url, new kakao.maps.Size(34, 42), {
    offset: new kakao.maps.Point(17, 42),
  });
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
    let settled = false;
    const finish = (callback, value) => {
      if (settled) {
        return;
      }
      settled = true;
      window.clearTimeout(timeoutId);
      callback(value);
    };
    const resolveSdk = () => {
      if (!window.kakao?.maps?.load) {
        finish(reject, new Error("카카오맵 SDK 초기화에 실패했습니다."));
        return;
      }
      window.kakao.maps.load(() => finish(resolve));
    };
    const rejectSdk = () => finish(reject, new Error("카카오맵 SDK 로드에 실패했습니다."));
    const timeoutId = window.setTimeout(
      () => finish(reject, new Error("카카오 JavaScript 키의 웹 플랫폼 도메인 등록을 확인해주세요.")),
      5000,
    );
    const existing = document.querySelector('script[data-kakao-map-sdk="true"]');
    if (existing) {
      if (existing.dataset.loaded === "true") {
        resolveSdk();
        return;
      }
      existing.addEventListener("load", resolveSdk, { once: true });
      existing.addEventListener("error", rejectSdk, { once: true });
      return;
    }

    const script = document.createElement("script");
    script.dataset.kakaoMapSdk = "true";
    script.async = true;
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${encodeURIComponent(key)}&autoload=false&libraries=services`;
    script.onload = () => {
      script.dataset.loaded = "true";
      resolveSdk();
    };
    script.onerror = rejectSdk;
    document.head.appendChild(script);
  });
}
</script>
