<template>
  <section class="kakao-map-panel">
    <div class="section-title-row">
      <div>
        <h2>현장과 추천 공급사 위치</h2>
        <p>공급사를 선택하면 현장에서 출발하는 차량 경로와 예상 시간을 확인합니다.</p>
      </div>
      <span>{{ validSuppliers.length }}개 공급사</span>
    </div>
    <div class="map-legend" aria-label="지도 위치 기준">
      <span v-if="hasValidSite" class="site">현장</span>
      <span class="actual">공급사 위치 {{ actualSupplierCount }}곳</span>
      <span class="estimated">참고·추정 위치 {{ estimatedSupplierCount }}곳</span>
    </div>
    <div class="kakao-map-frame">
      <div ref="mapElement" class="kakao-map-canvas" aria-label="추천 공급사 카카오맵"></div>
      <div v-if="siteWarning && !errorMessage" class="kakao-map-site-warning" role="status">
        {{ siteWarning }}
      </div>
      <div v-if="errorMessage" class="kakao-map-unavailable" role="status">
        <strong>지도를 표시할 수 없습니다.</strong>
        <span>{{ errorMessage }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  site: { type: Object, default: () => ({}) },
  suppliers: { type: Array, default: () => [] },
  selectedSupplier: { type: Object, default: null },
});
const emit = defineEmits(["select-supplier"]);

const mapElement = ref(null);
const errorMessage = ref("");
const siteWarning = ref("");
let renderSequence = 0;
let mapInstance = null;
let activeInfoWindow = null;
let activePolylineOutline = null;
let activePolyline = null;
let activeSelectedMarker = null;
let activeSelectedVariant = null;
let siteOverlay = null;
let renderedMarkers = [];
let supplierMarkers = new Map();
let supplierMarkerVariants = new Map();
const validSuppliers = computed(() =>
  props.suppliers.filter((supplier) => isKoreaMapCoordinate(supplier.latitude, supplier.longitude)),
);
const hasValidSite = computed(() => isKoreaMapCoordinate(props.site.latitude, props.site.longitude));
const actualSupplierCount = computed(() =>
  validSuppliers.value.filter((supplier) => supplier.locationBasis === "supplier_address").length,
);
const estimatedSupplierCount = computed(() =>
  validSuppliers.value.filter((supplier) =>
    ["contract_agency_estimated", "reference_estimated"].includes(supplier.locationBasis),
  ).length,
);

onMounted(renderMap);
watch(() => [props.site, props.suppliers], renderMap, { deep: true });
watch(() => props.selectedSupplier, renderSelectedSupplier, { deep: true });
onBeforeUnmount(() => {
  renderSequence += 1;
  clearRenderedMap();
});

async function renderMap() {
  const currentRender = ++renderSequence;
  await nextTick();
  try {
    await loadKakaoMapSdk();
    if (currentRender !== renderSequence || !mapElement.value) {
      return;
    }

    const kakao = window.kakao;
    const suppliers = validSuppliers.value;
    if (!hasValidSite.value && !suppliers.length) {
      errorMessage.value = "표시할 현장 또는 공급사 좌표가 없습니다.";
      return;
    }

    errorMessage.value = "";
    siteWarning.value = hasValidSite.value ? "" : "현장 좌표가 없어 차량 경로를 조회할 수 없습니다.";
    clearRenderedMap();
    const center = hasValidSite.value
      ? new kakao.maps.LatLng(Number(props.site.latitude), Number(props.site.longitude))
      : new kakao.maps.LatLng(Number(suppliers[0].latitude), Number(suppliers[0].longitude));
    const map = new kakao.maps.Map(mapElement.value, { center, level: 7 });
    mapInstance = map;
    const bounds = new kakao.maps.LatLngBounds();
    let boundsPointCount = 0;
    if (hasValidSite.value) {
      const sitePosition = new kakao.maps.LatLng(Number(props.site.latitude), Number(props.site.longitude));
      addMarker(kakao, map, sitePosition, `현장 · ${props.site.address || "주소 확인 필요"}`, "site");
      showSiteOverlay(kakao, map, sitePosition, props.site.address || "주소 확인 필요");
      bounds.extend(sitePosition);
      boundsPointCount += 1;
    }

    suppliers.forEach((supplier) => {
      const position = new kakao.maps.LatLng(Number(supplier.latitude), Number(supplier.longitude));
      addMarker(
        kakao,
        map,
        position,
        getSupplierMarkerText(supplier),
        getSupplierMarkerVariant(supplier),
        supplier,
      );
      bounds.extend(position);
      boundsPointCount += 1;
    });

    if (boundsPointCount > 1) {
      map.setBounds(bounds);
    }
    renderSelectedSupplier();

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
  const distanceM = Number(supplier.routeDistanceM ?? supplier.route_distance_m);
  const durationSec = Number(supplier.routeDurationSec ?? supplier.route_duration_sec);
  if (Number.isFinite(distanceM) && distanceM > 0 && Number.isFinite(durationSec) && durationSec > 0) {
    const minutes = Math.max(1, Math.round(durationSec / 60));
    const distanceKm = (distanceM / 1000).toFixed(1);
    return `${supplier.supplierName} · ${minutes}분 · ${distanceKm}km`;
  }

  const distanceText = supplier.routeNote || "거리 정보 확인 필요";

  if (supplier.locationBasis === "supplier_address") {
    return `${supplier.supplierName} · 공급사 위치 · ${distanceText}`;
  }

  if (supplier.locationBasis === "contract_agency_estimated") {
    return `${supplier.supplierName} · 계약기관 추정 위치 · ${distanceText}`;
  }

  if (supplier.locationBasis === "reference_estimated") {
    return `${supplier.supplierName} · 참고 위치 · ${distanceText}`;
  }

  return `${supplier.supplierName} · 위치 확인 필요 · ${distanceText}`;
}

function getSupplierMarkerVariant(supplier) {
  if (supplier.locationBasis === "supplier_address") {
    return "actual";
  }

  if (["contract_agency_estimated", "reference_estimated"].includes(supplier.locationBasis)) {
    return "estimated";
  }

  return "unknown";
}

function addMarker(kakao, map, position, text, variant = "actual", supplier = null) {
  const marker = new kakao.maps.Marker({
    map,
    position,
    image: createMarkerImage(kakao, variant),
  });
  renderedMarkers.push(marker);
  if (supplier) {
    const supplierKey = getSupplierKey(supplier);
    supplierMarkers.set(supplierKey, marker);
    supplierMarkerVariants.set(supplierKey, variant);
  }
  if (supplier) {
    kakao.maps.event.addListener(marker, "click", () => {
      clearActiveSelection();
      showInfoWindow(kakao, map, marker, text);
      emit("select-supplier", supplier);
    });
  }
}

function renderSelectedSupplier() {
  if (!mapInstance || !window.kakao?.maps || !props.selectedSupplier) {
    return;
  }
  const marker = supplierMarkers.get(getSupplierKey(props.selectedSupplier));
  if (!marker) {
    clearActiveSelection();
    return;
  }

  const kakao = window.kakao;
  clearActiveSelection();
  activeSelectedMarker = marker;
  activeSelectedVariant = supplierMarkerVariants.get(getSupplierKey(props.selectedSupplier)) || "unknown";
  marker.setImage(createMarkerImage(kakao, `selected-${activeSelectedVariant}`));
  supplierMarkers.forEach((supplierMarker) => {
    supplierMarker.setOpacity(supplierMarker === marker ? 1 : 0.6);
  });
  showInfoWindow(kakao, mapInstance, marker, getSupplierMarkerText(props.selectedSupplier));

  const routePath = Array.isArray(props.selectedSupplier.routePath)
    ? props.selectedSupplier.routePath
        .map((point) => ({ lat: Number(point.lat), lng: Number(point.lng) }))
        .filter((point) => Number.isFinite(point.lat) && Number.isFinite(point.lng))
    : [];
  if (props.selectedSupplier.routeStatus !== "success" || routePath.length < 2) {
    return;
  }

  const path = routePath.map((point) => new kakao.maps.LatLng(point.lat, point.lng));
  activePolylineOutline = new kakao.maps.Polyline({
    path,
    strokeWeight: 8,
    strokeColor: "#ffffff",
    strokeOpacity: 0.9,
    strokeStyle: "solid",
  });
  activePolylineOutline.setMap(mapInstance);

  activePolyline = new kakao.maps.Polyline({
    path,
    strokeWeight: 4,
    strokeColor: "#0b4fd4",
    strokeOpacity: 0.94,
    strokeStyle: "solid",
  });
  activePolyline.setMap(mapInstance);

  const bounds = new kakao.maps.LatLngBounds();
  path.forEach((point) => bounds.extend(point));
  mapInstance.setBounds(bounds);
}

function showInfoWindow(kakao, map, marker, text) {
  activeInfoWindow = new kakao.maps.InfoWindow({
    content: `<div class="map-info-window">${escapeMapText(text)}</div>`,
  });
  activeInfoWindow.open(map, marker);
}

function showSiteOverlay(kakao, map, position, address) {
  siteOverlay = new kakao.maps.CustomOverlay({
    map,
    position,
    yAnchor: 2.4,
    content: `<div class="map-site-label"><strong>현장</strong><span>${escapeMapText(address)}</span></div>`,
  });
}

function getSupplierKey(supplier) {
  return [
    supplier.dataSource || "",
    supplier.id || supplier.candidateId || "",
    supplier.supplierName || "",
    supplier.materialName || "",
    supplier.standard || "",
  ].join("|");
}

function escapeMapText(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function clearActiveSelection() {
  if (activeInfoWindow) {
    activeInfoWindow.close();
    activeInfoWindow = null;
  }
  if (activePolylineOutline) {
    activePolylineOutline.setMap(null);
    activePolylineOutline = null;
  }
  if (activePolyline) {
    activePolyline.setMap(null);
    activePolyline = null;
  }
  if (activeSelectedMarker && activeSelectedVariant && window.kakao?.maps) {
    activeSelectedMarker.setImage(createMarkerImage(window.kakao, activeSelectedVariant));
  }
  supplierMarkers.forEach((supplierMarker) => supplierMarker.setOpacity(1));
  activeSelectedMarker = null;
  activeSelectedVariant = null;
}

function clearRenderedMap() {
  clearActiveSelection();
  if (siteOverlay) {
    siteOverlay.setMap(null);
    siteOverlay = null;
  }
  renderedMarkers.forEach((marker) => marker.setMap(null));
  renderedMarkers = [];
  supplierMarkers.clear();
  supplierMarkerVariants.clear();
  mapInstance = null;
}

function createMarkerImage(kakao, variant) {
  const isSelected = variant.startsWith("selected-");
  const baseVariant = isSelected ? variant.replace("selected-", "") : variant;
  const colors = {
    site: "#1559e8",
    actual: "#0f766e",
    estimated: "#f97316",
    unknown: "#64748b",
  };
  const color = colors[baseVariant] || colors.unknown;
  const svg = baseVariant === "site" ? `
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
      <circle cx="18" cy="18" r="16.5" fill="${color}" stroke="#fff" stroke-width="3"/>
      <path fill="#fff" d="M10.5 17.5 18 10.7l7.5 6.8v7.8h-5v-5h-5v5h-5z"/>
    </svg>
  `.trim() : isSelected ? `
    <svg xmlns="http://www.w3.org/2000/svg" width="38" height="46" viewBox="0 0 38 46">
      <path fill="${color}" stroke="#fff" stroke-width="2.5" d="M19 1.5C9.3 1.5 1.5 9.2 1.5 18.7 1.5 31.6 19 44.5 19 44.5s17.5-12.9 17.5-25.8C36.5 9.2 28.7 1.5 19 1.5z"/>
      <circle cx="19" cy="18.5" r="7" fill="#fff"/>
      <circle cx="19" cy="18.5" r="3.5" fill="${color}"/>
    </svg>
  `.trim() : `
    <svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">
      <path fill="${color}" d="M17 0C7.6 0 0 7.5 0 16.8c0 12.6 17 25.2 17 25.2s17-12.6 17-25.2C34 7.5 26.4 0 17 0z"/>
      <circle cx="17" cy="16.8" r="6.8" fill="#fff"/>
    </svg>
  `.trim();
  const url = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  const width = baseVariant === "site" ? 36 : isSelected ? 38 : 34;
  const height = baseVariant === "site" ? 36 : isSelected ? 46 : 42;
  return new kakao.maps.MarkerImage(url, new kakao.maps.Size(width, height), {
    offset: new kakao.maps.Point(width / 2, height),
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
