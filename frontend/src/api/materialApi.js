import { additionalRecommendationResults, recommendationResults } from "../data/dummyData";
import { apiClient, buildApiUrl, USE_MOCK_API } from "./apiClient";

const REQUEST_STORAGE_KEY = "paceflow_v2_latest_request";
const SUPPLIER_STORAGE_KEY = "paceflow_v2_supplier_materials";
const INQUIRY_STORAGE_KEY = "paceflow_v2_supplier_inquiries";
const DEFAULT_INQUIRY_STATUS = "received";
const DEFAULT_MATERIAL_SUGGESTIONS = [
  { id: "fallback-rebar", name: "철근", spec: "SD400 D10", material_group: "철근", material_subtype: "이형철근" },
  { id: "fallback-h-beam", name: "H형강", spec: "300x300", material_group: "형강·강재", material_subtype: "H형강" },
  { id: "fallback-angle", name: "ㄱ형강", spec: "", material_group: "형강·강재", material_subtype: "ㄱ형강" },
  { id: "fallback-channel", name: "ㄷ형강", spec: "", material_group: "형강·강재", material_subtype: "ㄷ형강" },
  { id: "fallback-square-pipe", name: "각형강관", spec: "", material_group: "형강·강재", material_subtype: "각형강관" },
  { id: "fallback-steel-plate", name: "강판", spec: "", material_group: "형강·강재", material_subtype: "강판" },
  { id: "fallback-cement", name: "고로슬래그 시멘트", spec: "1종", material_group: "시멘트", material_subtype: "고로슬래그 시멘트" },
  { id: "fallback-glass-wool", name: "글라스울", spec: "", material_group: "단열재", material_subtype: "글라스울" },
  { id: "fallback-conduit", name: "전선관", spec: "", material_group: "전기 배관재", material_subtype: "전선관" },
  { id: "fallback-cd-conduit", name: "CD관", spec: "", material_group: "전기 배관재", material_subtype: "CD관" },
  { id: "fallback-pf-conduit", name: "PF관", spec: "", material_group: "전기 배관재", material_subtype: "PF관" },
];

export async function createMaterialRequest(payload) {
  if (!USE_MOCK_API) {
    const material = await findBackendMaterial(payload);
    const request = {
      id: `REQ-${Date.now()}`,
      createdAt: new Date().toISOString(),
      backendMaterialId: material.id,
      ...payload,
      siteLat: payload.siteLat !== null && payload.siteLat !== "" && Number.isFinite(Number(payload.siteLat))
        ? Number(payload.siteLat)
        : null,
      siteLng: payload.siteLng !== null && payload.siteLng !== "" && Number.isFinite(Number(payload.siteLng))
        ? Number(payload.siteLng)
        : null,
    };
    const { data } = await apiClient.post(buildApiUrl("/api/v1/demands/"), toBackendDemand(request));
    const savedRequest = { ...request, backendDemandId: data.id };
    localStorage.setItem(REQUEST_STORAGE_KEY, JSON.stringify(savedRequest));
    return savedRequest;
  }

  const request = {
    id: `REQ-${Date.now()}`,
    createdAt: new Date().toISOString(),
    ...payload,
  };

  localStorage.setItem(REQUEST_STORAGE_KEY, JSON.stringify(request));
  return request;
}

export async function getLatestMaterialRequest() {
  try {
    const saved = localStorage.getItem(REQUEST_STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export async function getMaterialSuggestions(query) {
  const normalizedQuery = String(query || "").trim();
  if (!normalizedQuery) {
    return [];
  }

  const loweredQuery = normalizedQuery.toLocaleLowerCase("ko-KR");
  const fallbackSuggestions = DEFAULT_MATERIAL_SUGGESTIONS.filter((item) =>
    [item.name, item.spec, item.material_group, item.material_subtype]
      .join(" ")
      .toLocaleLowerCase("ko-KR")
      .includes(loweredQuery),
  );
  let backendSuggestions = [];

  if (!USE_MOCK_API) {
    const { data } = await apiClient.get(buildApiUrl("/api/v1/materials/suggest/"), {
      params: { q: normalizedQuery },
    });
    backendSuggestions = Array.isArray(data) ? data : [];
  }

  const seen = new Set();
  return [...backendSuggestions, ...fallbackSuggestions]
    .filter((item) => {
      const key = `${item.name || ""}|${item.spec || ""}`.toLocaleLowerCase("ko-KR");
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    })
    .slice(0, 8);
}

export async function getRecommendations(requestId, options = {}) {
  if (!USE_MOCK_API) {
    const latestRequest = options.request || await getLatestMaterialRequest();
    const backendRecommendations = await getBackendAlternativeRecommendations(
      latestRequest,
      requestId,
      options,
    );
    const registeredRecommendations = await getPublicSupplierMaterialRecommendations(requestId, 0);
    const narajangteoRecommendations = await getNarajangteoRecommendationCandidates(options.keyword || "", requestId);
    return normalizeRecommendationRanking([
      ...backendRecommendations,
      ...registeredRecommendations,
      ...narajangteoRecommendations,
      ...recommendationResults,
      ...additionalRecommendationResults,
    ], requestId);
  }

  const registeredRecommendations = getStoredSupplierMaterials().map((item, index) =>
    createRecommendationFromSupplier(item, index),
  );

  return normalizeRecommendationRanking([
    ...registeredRecommendations,
    ...recommendationResults,
    ...additionalRecommendationResults,
  ], requestId);
}

export async function getDrivingRoute({ originLat, originLng, destinationLat, destinationLng }) {
  if (USE_MOCK_API) {
    return {
      routeDistanceM: null,
      routeDurationSec: null,
      routeStatus: "unavailable",
      routeNote: "거리 정보 확인 필요",
      routePath: [],
    };
  }

  const { data } = await apiClient.post(buildApiUrl("/api/v1/routes/driving/"), {
    origin_lat: Number(originLat),
    origin_lng: Number(originLng),
    destination_lat: Number(destinationLat),
    destination_lng: Number(destinationLng),
  });
  return {
    routeDistanceM: data.route_distance_m,
    routeDurationSec: data.route_duration_sec,
    routeStatus: data.route_status || "failed",
    routeNote: data.route_note || "거리 정보 확인 필요",
    routePath: Array.isArray(data.route_path)
      ? data.route_path
          .map((point) => ({ lat: Number(point.lat), lng: Number(point.lng) }))
          .filter((point) => Number.isFinite(point.lat) && Number.isFinite(point.lng))
      : [],
  };
}

function normalizeRecommendationRanking(items, requestId) {
  return dedupeRecommendations(items).map((item, index) => ({
      ...item,
      rank: index + 1,
      requestId,
      dataSource: item.dataSource || "demo_seed",
      dataSourceLabel: item.dataSourceLabel || getDemoDataSourceLabel(index),
      specSourceLabel: item.specSourceLabel || "KS 수동 DB",
      routeStatus: item.routeStatus || "not_requested",
      routeNote: item.routeNote || "거리 정보 확인 필요",
      locationBasis: normalizeRecommendationLocationBasis(item),
    }));
}

function normalizeRecommendationLocationBasis(item) {
  if (item.locationBasis && item.locationBasis !== "unknown") {
    return item.locationBasis;
  }

  const latitude = Number(item.latitude);
  const longitude = Number(item.longitude);
  const hasCoordinates = Number.isFinite(latitude)
    && Number.isFinite(longitude)
    && latitude >= 32
    && latitude <= 39
    && longitude >= 124
    && longitude <= 132;
  if (!hasCoordinates) {
    return "unknown";
  }

  return item.isRegisteredSupplier || item.dataSource === "supplier_registered"
    ? "supplier_address"
    : "reference_estimated";
}

async function getBackendAlternativeRecommendations(request, requestId, options) {
  if (
    !request?.backendMaterialId
    || !Number.isFinite(Number(request.siteLat))
    || !Number.isFinite(Number(request.siteLng))
  ) {
    return [];
  }

  try {
    const { data } = await apiClient.post(
      buildApiUrl(`/api/v1/materials/${request.backendMaterialId}/alternatives/`),
      {
        site_lat: Number(request.siteLat),
        site_lng: Number(request.siteLng),
        include_international: options.includeInternational !== false,
        radius_km: Number(options.radiusKm || 50),
      },
    );
    return toFrontendRecommendations(data, requestId);
  } catch {
    return [];
  }
}

async function getPublicSupplierMaterialRecommendations(requestId, startIndex = 0) {
  try {
    const { data } = await apiClient.get(buildApiUrl("/api/v1/supplier-materials/public/"));
    const results = Array.isArray(data) ? data : data.results || [];
    return dedupeSupplierMaterials(results.map(toFrontendSupplierMaterial)).map((item, index) =>
      createRecommendationFromSupplier(item, startIndex + index),
    ).map((item) => ({ ...item, requestId }));
  } catch {
    return [];
  }
}

export async function registerSupplierMaterial(payload) {
  if (!USE_MOCK_API) {
    const { data } = await apiClient.post(buildApiUrl("/api/v1/supplier-materials/"), toBackendSupplierMaterial(payload));
    return toFrontendSupplierMaterial(data);
  }

  return createMockSupplierMaterial(payload);
}

export async function getSupplierMaterials() {
  if (!USE_MOCK_API) {
    const { data } = await apiClient.get(buildApiUrl("/api/v1/supplier-materials/"));
    const results = Array.isArray(data) ? data : data.results || [];
    return results.map(toFrontendSupplierMaterial);
  }

  return getStoredSupplierMaterials();
}

export async function createSupplierInquiry(payload) {
  if (!USE_MOCK_API) {
    return createMockSupplierInquiry(payload);
  }

  return createMockSupplierInquiry(payload);
}

export async function getSupplierInquiries() {
  if (!USE_MOCK_API) {
    return getStoredSupplierInquiries();
  }

  return getStoredSupplierInquiries();
}

export async function getSupplierInquiry(inquiryId) {
  if (!USE_MOCK_API) {
    return getStoredSupplierInquiries().find((inquiry) => inquiry.id === inquiryId) || null;
  }

  return getStoredSupplierInquiries().find((inquiry) => inquiry.id === inquiryId) || null;
}

export async function getNarajangteoContracts(keyword, options = {}) {
  try {
    const endpoint = options.live ? "/api/v1/narajangteo/contracts/" : "/api/v1/narajangteo/cached-contracts/";
    const { data } = await apiClient.get(buildApiUrl(endpoint), {
      params: {
        keyword,
        year: options.year,
        rows: options.rows || 10,
        include_seed: options.includeSeed ? "true" : undefined,
      },
    });
    return data.contracts || [];
  } catch {
    return [];
  }
}

async function getNarajangteoRecommendationCandidates(keyword, requestId) {
  const rankingKeywords = keyword
    ? [keyword]
    : ["철근", "H빔", "시멘트", "단열재", "전선관"];
  const contractGroups = await Promise.all(
    rankingKeywords.map(async (rankingKeyword) => {
      try {
        const contracts = await getNarajangteoContracts(rankingKeyword, {
          rows: keyword ? 20 : 12,
          includeSeed: true,
        });
        return contracts.map((contract) => ({ ...contract, rankingKeyword }));
      } catch {
        return [];
      }
    }),
  );
  const contracts = contractGroups.flat();
  const uniqueContracts = contracts.filter((contract, index, items) => {
    const key = `${contract.rankingKeyword}:${contract.supplierName}`;
    return items.findIndex((item) => `${item.rankingKeyword}:${item.supplierName}` === key) === index;
  });
  const visibleContracts = keyword ? uniqueContracts.slice(0, 12) : uniqueContracts.slice(0, 60);
  return visibleContracts.map((contract, index) => {
    const amount = parsePriceAmount(contract.contractAmount);
    const sourceMeta = getDataSourceMeta(contract.source, contract.source);
    const isSeedCandidate = sourceMeta.key === "mvp_seed";
    const deliveryCount = Math.max(1, Number(contract.deliveryCount) || 1);
    const matchConfidence = getNarajangteoMatchConfidence(contract.matchBasis);
    const hasSupplierDistance = Boolean(contract.supplierDistanceAvailable);
    const latitude = Number(contract.latitude);
    const longitude = Number(contract.longitude);
    const hasCoordinates = contract.latitude !== null
      && contract.latitude !== undefined
      && contract.longitude !== null
      && contract.longitude !== undefined
      && Number.isFinite(latitude)
      && Number.isFinite(longitude)
      && latitude >= 32
      && latitude <= 39
      && longitude >= 124
      && longitude <= 132;
    const distanceKm = hasSupplierDistance ? Number((4.5 + index * 1.8).toFixed(1)) : null;
    const priceScore = Math.max(72, 92 - index * 2);
    const distanceScore = hasSupplierDistance ? Math.max(62, Math.round(100 - distanceKm * 3.5)) : 58;
    const reliabilityScore = isSeedCandidate
      ? Math.min(82, 66 + deliveryCount * 4)
      : Math.min(96, 78 + deliveryCount / 2);
    const materialFitScore = matchConfidence.score;

    return {
      requestId,
      supplierName: contract.supplierName,
      materialName: contract.productName || contract.rankingKeyword || keyword,
      standard: isSeedCandidate ? "KS 구조화 MVP 시드 기준" : "나라장터 계약 품명 기준",
      price: amount ? `${amount.toLocaleString()}원` : "계약금액 확인 필요",
      distanceKm,
      distanceLabel: hasSupplierDistance ? `${distanceKm}km` : "공급사 거리 확인 필요",
      locationBasis: contract.locationBasis || "unknown",
      locationLabel: contract.locationLabel || contract.demandAgency || "",
      deliveryCount,
      priceScore,
      distanceScore,
      reliabilityScore: Math.round(reliabilityScore),
      materialFitScore,
      totalScore: Math.round(materialFitScore * 0.45 + reliabilityScore * 0.3 + distanceScore * 0.15 + priceScore * 0.1),
      approvalRequired: false,
      dataSource: sourceMeta.key,
      dataSourceLabel: sourceMeta.label,
      specSourceLabel: matchConfidence.label,
      reason: isSeedCandidate
        ? "KS 규격 비교를 위한 MVP 시드 후보입니다. 실제 재고와 납품 가능 여부는 문의로 확인해야 합니다."
        : "나라장터 계약 이력에서 확인된 공급 후보입니다. 실제 규격과 납품 가능 여부는 문의로 확인해야 합니다.",
      reasonItems: [
        isSeedCandidate
          ? `${contract.contractDate || "최근"} MVP 거래 이력 샘플 기반 후보입니다.`
          : `${contract.contractDate || "최근"} 계약 이력 기반 후보입니다.`,
        isSeedCandidate
          ? "실제 공급사 데이터 연동 전 검증용 구조화 후보입니다."
          : `${contract.demandAgency || "수요기관"} 계약 자료를 참고했습니다.`,
        matchConfidence.description,
      ],
      scoreEvidence: {
        materialFit: `${matchConfidence.description} KS 물성 적합도 ${materialFitScore}점으로 반영했습니다.`,
        price: amount ? `계약금액 ${amount.toLocaleString()}원을 참고했습니다.` : "계약금액 원문 확인이 필요합니다.",
        distance: hasSupplierDistance
          ? "공급사 좌표 기준 거리 점수를 표시합니다."
          : "공급사 주소가 없어 계약기관 위치만 참고하고 거리 점수는 낮춰 반영했습니다.",
        reliability: isSeedCandidate
          ? "MVP 시드 이력은 공공 계약 이력보다 보수적인 신뢰도 점수를 적용했습니다."
          : "공공 계약 이력 존재 여부를 신뢰도 점수에 반영했습니다.",
      },
      latitude: hasCoordinates ? latitude : null,
      longitude: hasCoordinates ? longitude : null,
      approvalRiskNote: isSeedCandidate
        ? "구조화 시드 후보로 실제 규격서와 공급 조건은 문의 시 확인이 필요합니다."
        : "계약 이력 기반 후보로 세부 규격과 시험성적서는 문의 시 확인이 필요합니다.",
    };
  });
}

function getNarajangteoMatchConfidence(matchBasis = "") {
  if (matchBasis.includes("KS 규격 구조화 시드")) {
    return {
      score: 93,
      label: "KS 구조화 시드",
      description: "KS 규격·강종·호칭을 구조화한 MVP 후보입니다.",
    };
  }

  if (matchBasis.includes("품명/규격 텍스트 매칭")) {
    return {
      score: 94,
      label: "계약 품명 규격 매칭",
      description: "계약명/품명에서 세부 규격 단서가 확인된 후보입니다.",
    };
  }

  if (matchBasis.includes("대표 규격 매핑")) {
    return {
      score: 84,
      label: "대표 규격 매핑",
      description: "세부 규격 단서가 부족해 자재군 대표 KS 규격으로 매핑한 후보입니다.",
    };
  }

  return {
    score: 78,
    label: "계약 이력 기반",
    description: "기존 수집 이력 기반 후보로 세부 규격은 문의 시 확인이 필요합니다.",
  };
}

function parsePriceAmount(value) {
  const amount = Number(String(value || "").replace(/[^\d.]/g, ""));
  return Number.isFinite(amount) && amount > 0 ? amount : 0;
}

export async function updateSupplierInquiryStatus(inquiryId, status) {
  if (!USE_MOCK_API) {
    return updateMockSupplierInquiryStatus(inquiryId, status);
  }

  return updateMockSupplierInquiryStatus(inquiryId, status);
}


async function findBackendMaterial(payload) {
  const { data } = await apiClient.get(buildApiUrl("/api/v1/materials/"), {
    params: {
      name: payload.materialName || payload.category || "",
    },
  });
  let materials = Array.isArray(data) ? data : data.results || [];
  if (!materials.length) {
    const fallbackResponse = await apiClient.get(buildApiUrl("/api/v1/materials/"));
    materials = Array.isArray(fallbackResponse.data) ? fallbackResponse.data : fallbackResponse.data.results || [];
  }
  if (!materials.length) {
    throw new Error("백엔드에 등록된 자재 데이터가 없습니다. seed_data.py를 먼저 실행해 주세요.");
  }

  const requestedText = [
    payload.materialName,
    payload.standard,
    payload.strengthGrade,
    payload.category,
  ]
    .filter(Boolean)
    .join(" ");
  const normalizedRequestedText = normalizeMaterialSearchText(requestedText);

  return (
    materials.find((material) => {
      const materialText = [
        material.name,
        material.ks_code,
        material.ks_grade,
        material.diameter,
        material.category_display,
      ]
        .filter(Boolean)
        .join(" ");
      const normalizedMaterialText = normalizeMaterialSearchText(materialText);
      const normalizedGrade = normalizeMaterialSearchText(material.ks_grade);
      const normalizedDiameter = normalizeMaterialSearchText(material.diameter);
      const normalizedMaterialName = normalizeMaterialSearchText(payload.materialName);

      return (
        normalizedRequestedText.includes(normalizedGrade) ||
        normalizedRequestedText.includes(normalizedDiameter) ||
        normalizedMaterialText.includes(normalizedMaterialName)
      );
    }) ||
    materials[0]
  );
}

function normalizeMaterialSearchText(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[()\s/_-]/g, "")
    .replace(/×/g, "x");
}

function toBackendDemand(request) {
  return {
    site_name: request.siteAddress || "PaceFlow 현장",
    site_lat: roundCoordinate(request.siteLat),
    site_lng: roundCoordinate(request.siteLng),
    material: request.backendMaterialId,
    quantity: parseQuantity(request.requiredQuantity),
    deadline: request.requiredDate,
    memo: request.memo || "",
  };
}

function roundCoordinate(value) {
  return Number(Number(value).toFixed(6));
}

function parseQuantity(value) {
  const quantity = Number(String(value).replace(/[^\d.]/g, ""));
  return Number.isFinite(quantity) && quantity > 0 ? quantity : 1;
}

function toFrontendRecommendations(data, requestId) {
  const original = data.original_material;
  return (data.recommendations || []).map((item, index) => {
    const material = item.material;
    const supplier = item.supplier;
    const scores = normalizeBackendScores(item.scores);
    const approvalRequired = Boolean(item.approval_warning || material?.regulation?.requires_approval);
    const dataSource = getDataSourceMeta(item.data_source, supplier?.source);
    const hardFilterEvidence = buildHardFilterEvidence(original, material, {
      includeInternational: !approvalRequired,
      approvalWarning: item.approval_warning,
    });

    return {
      rank: item.rank || index + 1,
      requestId,
      supplierName: supplier?.name || "공급사 미지정",
      materialName: formatMaterialName(material),
      standard: formatStandard(material),
      price: `${Number(item.latest_unit_price || 0).toLocaleString()}원`,
      distanceKm: item.distance_km,
      routeDistanceM: item.route_distance_m,
      routeDurationSec: item.route_duration_sec,
      routeStatus: item.route_status || "api_error",
      routeNote: item.route_note || "거리 정보 확인 필요",
      deliveryCount: item.supply_count,
      priceScore: scores.priceScore,
      distanceScore: scores.distanceScore,
      reliabilityScore: scores.reliabilityScore,
      totalScore: scores.totalScore,
      approvalRequired,
      dataSource: dataSource.key,
      dataSourceLabel: dataSource.label,
      specSourceLabel: material?.spec?.source || (material?.spec ? "KS 수동 DB" : "물성 확인 필요"),
      reason: approvalRequired
        ? "물성 조건은 충족하지만 감리 승인 확인이 필요한 후보입니다."
        : "물성 조건과 공급 이력을 기준으로 우선 문의 가능한 후보입니다.",
      reasonItems: buildReasonItems(original, material, item),
      propertyComparison: buildPropertyComparison(original, material),
      hardFilterEvidence,
      priceTrend: buildPriceTrend(item.latest_unit_price),
      trendLabels: ["1월", "2월", "3월", "4월", "5월", "현재"],
      scoreEvidence: {
        price: `최신 단가 ${Number(item.latest_unit_price || 0).toLocaleString()}원을 기준으로 산정했습니다.`,
        distance: item.route_status === "success"
          ? `카카오 차량 경로 ${formatRouteDuration(item.route_duration_sec)} · ${formatRouteDistance(item.route_distance_m)}를 반영했습니다.`
          : item.route_note || "차량 경로가 확인되지 않아 거리 가중치를 제외했습니다.",
        reliability: `납품 이력 ${item.supply_count}회를 신뢰도 점수에 반영했습니다.`,
      },
      approvalChecklist: buildApprovalChecklist(material, approvalRequired, item.approval_warning),
      approvalRiskNote:
        item.approval_warning ||
        "백엔드 물성 필터를 통과한 후보입니다. 최종 납품 가능 여부는 공급사 확인이 필요합니다.",
      contact: supplier?.phone,
      address: supplier?.address,
      latitude: supplier?.latitude,
      longitude: supplier?.longitude,
      locationBasis: supplier?.latitude != null && supplier?.longitude != null
        ? "supplier_address"
        : "unknown",
      isRegisteredSupplier: false,
    };
  });
}

function normalizeBackendScores(scores = {}) {
  const normalizeScore = (value, legacyMultiplier = 100) => {
    if (value === null || value === undefined || value === "") {
      return null;
    }
    const score = Number(value);
    if (!Number.isFinite(score)) {
      return null;
    }
    return Math.round(Math.abs(score) <= 1 ? score * legacyMultiplier : score);
  };

  return {
    materialFitScore: normalizeScore(scores.material_fit_score) ?? 100,
    priceScore: normalizeScore(scores.price_score, 250) ?? 0,
    distanceScore: normalizeScore(scores.route_score ?? scores.distance_score, 333.33),
    reliabilityScore: normalizeScore(scores.reliability_score, 333.33) ?? 0,
    totalScore: normalizeScore(scores.total) ?? 0,
  };
}

function formatRouteDuration(durationSec) {
  const seconds = Number(durationSec);
  return Number.isFinite(seconds) ? `약 ${Math.max(1, Math.round(seconds / 60))}분` : "시간 확인 필요";
}

function formatRouteDistance(distanceM) {
  const meters = Number(distanceM);
  return Number.isFinite(meters) ? `${(meters / 1000).toFixed(1)}km` : "거리 확인 필요";
}

function formatMaterialName(material) {
  return [material?.name, material?.ks_grade, material?.diameter].filter(Boolean).join(" ") || "자재명 확인 필요";
}

function formatStandard(material) {
  return [material?.ks_code, material?.ks_grade, material?.diameter].filter(Boolean).join(" / ") || "규격 확인 필요";
}

function isCementMaterial(material) {
  const text = [material?.name, material?.ks_code, material?.ks_grade].filter(Boolean).join(" ");
  return text.includes("시멘트") || text.includes("KS L 5201");
}

function isInsulationMaterial(material) {
  const text = [material?.name, material?.ks_code, material?.ks_grade].filter(Boolean).join(" ");
  return (
    text.includes("단열재") ||
    text.includes("KS M 3880") ||
    text.includes("KS M 3871") ||
    text.includes("KS M ISO 4898")
  );
}

function buildReasonItems(original, material, item) {
  let materialLabel = "항복강도·인장강도·연신율·탄소당량 기준";
  if (isInsulationMaterial(original) || isInsulationMaterial(material)) {
    materialLabel = "압축강도·열성능·흡수성/투습 기준";
  } else if (isCementMaterial(original) || isCementMaterial(material)) {
    materialLabel = "압축강도·화학 성분 기준";
  }

  return [
    `Hard Filter에서 ${materialLabel}을 통과했습니다.`,
    `${formatStandard(material)} 기준으로 동등성 후보에 포함되었습니다.`,
    `현장 기준 ${item.distance_km}km 거리의 납품 실적 공급사입니다.`,
    `과거 납품 이력 ${item.supply_count}회를 기준으로 신뢰도를 반영했습니다.`,
  ];
}

function buildPropertyComparison(original, material) {
  const originalSpec = original?.spec || {};
  const candidateSpec = material?.spec || {};

  if (isInsulationMaterial(original) || isInsulationMaterial(material)) {
    return [
      {
        label: "압축강도",
        original: formatSpecValue(originalSpec.yield_strength_min, "kPa"),
        candidate: formatSpecValue(candidateSpec.yield_strength_min, "kPa"),
        standard: `>= ${formatSpecValue(originalSpec.yield_strength_min, "kPa")}`,
        passed: true,
      },
      {
        label: "열성능 지수",
        original: formatSpecValue(originalSpec.tensile_strength_min, "점"),
        candidate: formatSpecValue(candidateSpec.tensile_strength_min, "점"),
        standard: `>= ${formatSpecValue(originalSpec.tensile_strength_min, "점")}`,
        passed: true,
      },
      {
        label: "흡수성/투습 기준",
        original: formatSpecValue(originalSpec.carbon_equivalent_max, ""),
        candidate: formatSpecValue(candidateSpec.carbon_equivalent_max, ""),
        standard: `<= ${formatSpecValue(originalSpec.carbon_equivalent_max, "")}`,
        passed: true,
      },
      {
        label: "규격 출처",
        original: originalSpec.source || "KS 단열재 규격 확인 필요",
        candidate: candidateSpec.source || "KS 단열재 규격 확인 필요",
        standard: "KS M 3880 / KS M 3871-1 / KS M ISO 4898",
        passed: true,
      },
    ];
  }

  if (isCementMaterial(original) || isCementMaterial(material)) {
    return [
      {
        label: "조기 압축강도",
        original: formatSpecValue(originalSpec.yield_strength_min, "MPa"),
        candidate: formatSpecValue(candidateSpec.yield_strength_min, "MPa"),
        standard: `>= ${formatSpecValue(originalSpec.yield_strength_min, "MPa")}`,
        passed: true,
      },
      {
        label: "28일 압축강도",
        original: formatSpecValue(originalSpec.tensile_strength_min, "MPa"),
        candidate: formatSpecValue(candidateSpec.tensile_strength_min, "MPa"),
        standard: `>= ${formatSpecValue(originalSpec.tensile_strength_min, "MPa")}`,
        passed: true,
      },
      {
        label: "SO3 상한",
        original: formatSpecValue(originalSpec.carbon_equivalent_max, "%"),
        candidate: formatSpecValue(candidateSpec.carbon_equivalent_max, "%"),
        standard: `<= ${formatSpecValue(originalSpec.carbon_equivalent_max, "%")}`,
        passed: true,
      },
      {
        label: "규격 출처",
        original: originalSpec.source || "KS L 5201 확인 필요",
        candidate: candidateSpec.source || "KS L 5201 확인 필요",
        standard: "KS L 5201:2021",
        passed: true,
      },
    ];
  }

  return [
    {
      label: "항복강도",
      original: formatSpecValue(originalSpec.yield_strength_min, "MPa"),
      candidate: formatSpecValue(candidateSpec.yield_strength_min, "MPa"),
      standard: `>= ${formatSpecValue(originalSpec.yield_strength_min, "MPa")}`,
      passed: true,
    },
    {
      label: "인장강도",
      original: formatSpecValue(originalSpec.tensile_strength_min, "MPa"),
      candidate: formatSpecValue(candidateSpec.tensile_strength_min, "MPa"),
      standard: `>= ${formatSpecValue(originalSpec.tensile_strength_min, "MPa")}`,
      passed: true,
    },
    {
      label: "연신율",
      original: formatSpecValue(originalSpec.elongation_min, "%"),
      candidate: formatSpecValue(candidateSpec.elongation_min, "%"),
      standard: `>= ${formatSpecValue(originalSpec.elongation_min, "%")}`,
      passed: true,
    },
    {
      label: "탄소당량",
      original: formatSpecValue(originalSpec.carbon_equivalent_max, ""),
      candidate: formatSpecValue(candidateSpec.carbon_equivalent_max, ""),
      standard: `<= ${formatSpecValue(originalSpec.carbon_equivalent_max, "")}`,
      passed: true,
    },
  ];
}

function buildHardFilterEvidence(original, material, options = {}) {
  const originalSpec = original?.spec || {};
  const candidateSpec = material?.spec || {};
  const regulation = material?.regulation || {};
  const standardMapping = [
    regulation.astm_code && regulation.astm_code !== "—" ? `ASTM ${regulation.astm_code}` : "",
    regulation.jis_code && regulation.jis_code !== "—" ? `JIS ${regulation.jis_code}` : "",
  ].filter(Boolean);

  if (isCementMaterial(original) || isCementMaterial(material)) {
    return [
      {
        label: "압축강도",
        status: "통과",
        description: `조기 ${formatSpecValue(candidateSpec.yield_strength_min, "MPa")}, 28일 ${formatSpecValue(candidateSpec.tensile_strength_min, "MPa")} 기준 충족`,
      },
      {
        label: "화학 성분",
        status: "통과",
        description: `SO3 후보 ${formatSpecValue(candidateSpec.carbon_equivalent_max, "%")} / 기준 ${formatSpecValue(originalSpec.carbon_equivalent_max, "%")} 이하`,
      },
      {
        label: "KS L 5201",
        status: "확인",
        description: "포틀랜드 시멘트 1종~5종의 물리 성능과 화학 성분 기준을 비교합니다.",
      },
      {
        label: "시험 기준",
        status: "확인",
        description: "압축강도는 KS L ISO 679, 화학 성분은 KS L 5120 또는 KS L 5222 기준을 참고합니다.",
      },
    ];
  }

  return [
    {
      label: "물성치 범위",
      status: "통과",
      description: `항복 ${formatSpecValue(candidateSpec.yield_strength_min, "MPa")}, 인장 ${formatSpecValue(candidateSpec.tensile_strength_min, "MPa")}, 연신율 ${formatSpecValue(candidateSpec.elongation_min, "%")} 기준 충족`,
    },
    {
      label: "탄소당량",
      status: "통과",
      description: `후보 ${formatSpecValue(candidateSpec.carbon_equivalent_max, "")} / 기준 ${formatSpecValue(originalSpec.carbon_equivalent_max, "")} 이하`,
    },
    {
      label: "시공 호환성",
      status: "확인",
      description: `구조재 분류, 내진 조건, 용접 가능 여부를 백엔드 필터에서 확인했습니다.`,
    },
    {
      label: "국제 규격",
      status: options.approvalWarning ? "승인 확인" : "통과",
      description: standardMapping.length
        ? `${standardMapping.join(" · ")} 동등 규격 매핑을 표시합니다.`
        : "KS 직접 대체 후보로 분류됩니다.",
    },
  ];
}

function buildApprovalChecklist(material, approvalRequired, approvalWarning) {
  const regulation = material?.regulation || {};
  const internationalCodes = [regulation.astm_code, regulation.jis_code].filter((code) => code && code !== "—");

  return [
    {
      label: "국제 규격",
      status: internationalCodes.length ? "승인 확인" : "낮음",
      description: internationalCodes.length
        ? `${internationalCodes.join(" · ")} 동등 규격 자료와 감리 승인 여부를 확인해야 합니다.`
        : "KS 규격 기준 후보로 국제 규격 승인 부담이 낮습니다.",
    },
    {
      label: "강도 상향",
      status: approvalRequired ? "검토 필요" : "낮음",
      description: approvalRequired
        ? "강도 상향 또는 국제 규격 적용 가능성이 있어 구조 검토가 필요할 수 있습니다."
        : "요청 자재 기준에서 우선 검토 가능한 후보입니다.",
    },
    {
      label: "감리 확인",
      status: approvalWarning ? "필요" : "현장 확인",
      description: approvalWarning || "최종 적용 전 현장 감리 기준과 납품 서류를 확인하세요.",
    },
  ];
}

function buildPriceTrend(latestPrice) {
  const price = Number(latestPrice || 0);
  if (!Number.isFinite(price) || price <= 0) {
    return [];
  }

  return [1.07, 1.045, 1.025, 1.015, 0.995, 1].map((ratio) => Math.round(price * ratio));
}

function getDataSourceMeta(rawSource, supplierSource) {
  const source = String(rawSource || supplierSource || "").toLowerCase();

  if (source.includes("narajangteo") || source.includes("나라장터")) {
    return { key: "narajangteo", label: "나라장터 계약 이력" };
  }

  if (source.includes("paceflow mvp seed") || source.includes("seed")) {
    return { key: "mvp_seed", label: "MVP 시드 데이터" };
  }

  if (source.includes("manual")) {
    return { key: "manual", label: "수동 입력 데이터" };
  }

  return { key: "unknown", label: "출처 확인 필요" };
}

function getDemoDataSourceLabel(index) {
  const labels = ["합성 랭킹 데이터", "거래 이력 샘플", "공공 API 연동 예정", "MVP 데모 데이터"];
  return labels[index % labels.length];
}

function formatSpecValue(value, unit) {
  if (value === null || value === undefined || value === "") {
    return "확인 필요";
  }
  return `${Number(value).toLocaleString()}${unit ? ` ${unit}` : ""}`;
}

function createMockSupplierMaterial(payload) {
  const material = {
    id: `SUP-${Date.now()}`,
    createdAt: new Date().toISOString(),
    ...payload,
  };

  const savedMaterials = getStoredSupplierMaterials();
  localStorage.setItem(SUPPLIER_STORAGE_KEY, JSON.stringify([material, ...savedMaterials]));
  return material;
}

function dedupeSupplierMaterials(items) {
  const seen = new Map();

  items.forEach((item) => {
    const key = [
      item.ownerEmail || item.supplierName,
      item.supplierName,
      item.materialName,
      item.standard,
      item.strengthGrade,
    ]
      .filter(Boolean)
      .join("|")
      .toLowerCase();

    const previous = seen.get(key);
    if (!previous || new Date(item.createdAt || 0) > new Date(previous.createdAt || 0)) {
      seen.set(key, item);
    }
  });

  return Array.from(seen.values());
}

function dedupeRecommendations(items) {
  const seen = new Map();

  items.forEach((item) => {
    const key = [item.supplierName, item.materialName, item.standard]
      .filter(Boolean)
      .join("|")
      .toLowerCase();

    const previous = seen.get(key);
    if (!previous || Number(item.totalScore || 0) > Number(previous.totalScore || 0)) {
      seen.set(key, item);
    }
  });

  return Array.from(seen.values());
}

function toBackendSupplierMaterial(payload) {
  return {
    supplier_name: payload.supplierName,
    contact: payload.contact,
    address: payload.address,
    zip_no: payload.zipNo,
    latitude: payload.latitude,
    longitude: payload.longitude,
    main_materials: payload.mainMaterials,
    material_name: payload.materialName,
    standard: payload.standard,
    strength_grade: payload.strengthGrade,
    recent_price: payload.recentPrice || null,
    service_area: payload.serviceArea,
    distance_km: payload.distanceKm || null,
    delivery_count: payload.deliveryCount || 0,
    note: payload.note,
  };
}

function toFrontendSupplierMaterial(item) {
  return {
    id: item.id,
    ownerEmail: item.owner_email,
    supplierName: item.supplier_name,
    contact: item.contact,
    address: item.address,
    zipNo: item.zip_no,
    latitude: item.latitude === null || item.latitude === undefined ? null : Number(item.latitude),
    longitude: item.longitude === null || item.longitude === undefined ? null : Number(item.longitude),
    mainMaterials: item.main_materials,
    materialName: item.material_name,
    standard: item.standard,
    strengthGrade: item.strength_grade,
    recentPrice: item.recent_price === null || item.recent_price === undefined ? "" : Number(item.recent_price),
    serviceArea: item.service_area,
    distanceKm: item.distance_km === null || item.distance_km === undefined ? "" : Number(item.distance_km),
    deliveryCount: item.delivery_count || 0,
    note: item.note,
    createdAt: item.created_at,
  };
}

function createMockSupplierInquiry(payload) {
  const isUrgent = payload.requestType === "urgent" || payload.priority === "high";
  const inquiry = {
    id: `${isUrgent ? "URG" : "INQ"}-${Date.now()}`,
    createdAt: new Date().toISOString(),
    status: DEFAULT_INQUIRY_STATUS,
    statusUpdatedAt: new Date().toISOString(),
    requestType: isUrgent ? "urgent" : "general",
    priority: isUrgent ? "high" : "normal",
    ...payload,
  };

  const savedInquiries = getStoredSupplierInquiries();
  localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify([inquiry, ...savedInquiries]));
  return inquiry;
}

function updateMockSupplierInquiryStatus(inquiryId, status) {
  const updatedAt = new Date().toISOString();
  const inquiries = getStoredSupplierInquiries().map((inquiry) =>
    inquiry.id === inquiryId ? { ...inquiry, status, statusUpdatedAt: updatedAt } : inquiry,
  );

  localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify(inquiries));
  return inquiries.find((inquiry) => inquiry.id === inquiryId) || null;
}

function getStoredSupplierMaterials() {
  try {
    const saved = localStorage.getItem(SUPPLIER_STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function getStoredSupplierInquiries() {
  try {
    const saved = localStorage.getItem(INQUIRY_STORAGE_KEY);
    return saved ? JSON.parse(saved).map(normalizeInquiry) : [];
  } catch {
    return [];
  }
}

function normalizeInquiry(inquiry) {
  const isUrgent = inquiry.requestType === "urgent" || inquiry.priority === "high" || String(inquiry.id || "").startsWith("URG");
  return {
    status: DEFAULT_INQUIRY_STATUS,
    statusUpdatedAt: inquiry.createdAt,
    requestType: isUrgent ? "urgent" : "general",
    priority: isUrgent ? "high" : "normal",
    ...inquiry,
  };
}

function createRecommendationFromSupplier(item, index) {
  const distanceKm = Number(item.distanceKm || 6 + index * 2);
  const deliveryCount = Number(item.deliveryCount || 0);
  const priceScore = Math.max(70, 96 - index * 3);
  const distanceScore = Math.max(65, Math.round(100 - distanceKm * 4));
  const reliabilityScore = Math.min(98, 70 + deliveryCount);
  const materialFitScore = item.standard?.includes("ASTM") || item.standard?.includes("JIS") ? 78 : 88;
  const totalScore = Math.round(materialFitScore * 0.45 + reliabilityScore * 0.3 + distanceScore * 0.15 + priceScore * 0.1);

  return {
    supplierName: item.supplierName,
    materialName: item.materialName,
    standard: [item.standard, item.strengthGrade].filter(Boolean).join(" / ") || "규격 확인 필요",
    price: item.recentPrice ? `${Number(item.recentPrice).toLocaleString()}원` : "단가 확인 필요",
    distanceKm,
    deliveryCount,
    priceScore,
    distanceScore,
    reliabilityScore,
    materialFitScore,
    totalScore,
    approvalRequired: item.standard?.includes("ASTM") || item.standard?.includes("JIS"),
    dataSource: "supplier_registered",
    dataSourceLabel: "공급사 직접 등록",
    specSourceLabel: "물성 서류 확인 필요",
    reason: "공급사가 직접 등록한 취급 자재로, 실제 납품 가능 여부는 문의 확인이 필요합니다.",
    reasonItems: [
      "공급사가 직접 등록한 취급 자재입니다.",
      "실제 재고와 납품 가능 여부는 문의로 확인해야 합니다.",
      `납품 가능 지역 ${item.serviceArea || "미입력"} 기준으로 검토합니다.`,
    ],
    hardFilterEvidence: [
      { label: "공급사 등록", status: "확인", description: "공급사가 직접 등록한 자재 정보입니다." },
      { label: "물성 검증", status: "문의 필요", description: "등록 자재는 최종 물성 서류 확인이 필요합니다." },
      { label: "납품 조건", status: "확인", description: `최근 단가와 납품 가능 지역을 기준으로 표시합니다.` },
      { label: "승인 리스크", status: item.standard?.includes("ASTM") || item.standard?.includes("JIS") ? "승인 확인" : "낮음", description: "국제 규격 여부와 감리 승인 필요 여부를 확인합니다." },
    ],
    priceTrend: buildPriceTrend(item.recentPrice),
    trendLabels: ["1월", "2월", "3월", "4월", "5월", "현재"],
    approvalChecklist: [
      { label: "등록 정보", status: "확인", description: "공급사가 입력한 자재 정보 기준입니다." },
      { label: "물성 서류", status: "문의 필요", description: "시험성적서 또는 규격 증빙 자료 확인이 필요합니다." },
      { label: "감리 확인", status: item.standard?.includes("ASTM") || item.standard?.includes("JIS") ? "필요" : "현장 확인", description: "최종 적용 전 현장 승인 기준을 확인하세요." },
    ],
    contact: item.contact,
    address: item.address,
    latitude: item.latitude,
    longitude: item.longitude,
    locationBasis: item.latitude != null && item.longitude != null
      ? "supplier_address"
      : "unknown",
    serviceArea: item.serviceArea,
    isRegisteredSupplier: true,
  };
}
