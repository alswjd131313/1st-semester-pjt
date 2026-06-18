import { recommendationResults } from "../data/dummyData";
import { apiClient, buildApiUrl, USE_MOCK_API } from "./apiClient";

const REQUEST_STORAGE_KEY = "paceflow_v2_latest_request";
const SUPPLIER_STORAGE_KEY = "paceflow_v2_supplier_materials";
const INQUIRY_STORAGE_KEY = "paceflow_v2_supplier_inquiries";
const DEFAULT_INQUIRY_STATUS = "received";

export async function createMaterialRequest(payload) {
  if (!USE_MOCK_API) {
    const material = await findBackendMaterial(payload);
    const request = {
      id: `REQ-${Date.now()}`,
      createdAt: new Date().toISOString(),
      backendMaterialId: material.id,
      ...payload,
      siteLat: payload.siteLat || DEFAULT_SITE_LAT,
      siteLng: payload.siteLng || DEFAULT_SITE_LNG,
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

export async function getRecommendations(requestId) {
  if (!USE_MOCK_API) {
    const request = await getLatestMaterialRequest();
    if (!request?.backendMaterialId) {
      throw new Error("추천 조회에 필요한 백엔드 자재 ID가 없습니다.");
    }

    const { data } = await apiClient.post(
      buildApiUrl(`/api/v1/materials/${request.backendMaterialId}/alternatives/`),
      {
        site_lat: request.siteLat || DEFAULT_SITE_LAT,
        site_lng: request.siteLng || DEFAULT_SITE_LNG,
        is_seismic: true,
        include_international: true,
      },
    );
    return toFrontendRecommendations(data, requestId);
  }

  const registeredRecommendations = getStoredSupplierMaterials().map((item, index) =>
    createRecommendationFromSupplier(item, index),
  );

  return [...registeredRecommendations, ...recommendationResults].map((item, index) => ({
    ...item,
    rank: index + 1,
    requestId,
  }));
}

export async function registerSupplierMaterial(payload) {
  if (!USE_MOCK_API) {
    return createMockSupplierMaterial(payload);
  }

  return createMockSupplierMaterial(payload);
}

export async function getSupplierMaterials() {
  if (!USE_MOCK_API) {
    return getStoredSupplierMaterials();
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

export async function updateSupplierInquiryStatus(inquiryId, status) {
  if (!USE_MOCK_API) {
    return updateMockSupplierInquiryStatus(inquiryId, status);
  }

  return updateMockSupplierInquiryStatus(inquiryId, status);
}

const DEFAULT_SITE_LAT = 37.5447;
const DEFAULT_SITE_LNG = 127.0558;

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
      return requestedText.includes(material.ks_grade) || requestedText.includes(material.diameter) || materialText.includes(payload.materialName);
    }) ||
    materials[0]
  );
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

    return {
      rank: item.rank || index + 1,
      requestId,
      supplierName: supplier?.name || "공급사 미지정",
      materialName: formatMaterialName(material),
      standard: formatStandard(material),
      price: `${Number(item.latest_unit_price || 0).toLocaleString()}원`,
      distanceKm: item.distance_km,
      deliveryCount: item.supply_count,
      priceScore: scores.priceScore,
      distanceScore: scores.distanceScore,
      reliabilityScore: scores.reliabilityScore,
      totalScore: scores.totalScore,
      approvalRequired,
      reason: approvalRequired
        ? "물성 조건은 충족하지만 감리 승인 확인이 필요한 후보입니다."
        : "물성 조건과 공급 이력을 기준으로 우선 문의 가능한 후보입니다.",
      reasonItems: [
        `${formatStandard(material)} 기준으로 동등성 후보에 포함되었습니다.`,
        `현장 기준 ${item.distance_km}km 거리의 납품 실적 공급사입니다.`,
        `과거 납품 이력 ${item.supply_count}회를 기준으로 신뢰도를 반영했습니다.`,
      ],
      propertyComparison: buildPropertyComparison(original, material),
      scoreEvidence: {
        price: `최신 단가 ${Number(item.latest_unit_price || 0).toLocaleString()}원을 기준으로 산정했습니다.`,
        distance: `현장 좌표와 공급사 좌표 사이 거리 ${item.distance_km}km를 반영했습니다.`,
        reliability: `납품 이력 ${item.supply_count}회를 신뢰도 점수에 반영했습니다.`,
      },
      approvalRiskNote:
        item.approval_warning ||
        "백엔드 물성 필터를 통과한 후보입니다. 최종 납품 가능 여부는 공급사 확인이 필요합니다.",
      contact: supplier?.phone,
      address: supplier?.address,
      latitude: supplier?.latitude,
      longitude: supplier?.longitude,
      isRegisteredSupplier: false,
    };
  });
}

function normalizeBackendScores(scores = {}) {
  return {
    priceScore: Math.round(Number(scores.price_score || 0) * 250),
    distanceScore: Math.round(Number(scores.distance_score || 0) * 333.33),
    reliabilityScore: Math.round(Number(scores.reliability_score || 0) * 333.33),
    totalScore: Math.round(Number(scores.total || 0) * 100),
  };
}

function formatMaterialName(material) {
  return [material?.name, material?.ks_grade, material?.diameter].filter(Boolean).join(" ") || "자재명 확인 필요";
}

function formatStandard(material) {
  return [material?.ks_code, material?.ks_grade, material?.diameter].filter(Boolean).join(" / ") || "규격 확인 필요";
}

function buildPropertyComparison(original, material) {
  const originalSpec = original?.spec || {};
  const candidateSpec = material?.spec || {};
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

function createMockSupplierInquiry(payload) {
  const inquiry = {
    id: `INQ-${Date.now()}`,
    createdAt: new Date().toISOString(),
    status: DEFAULT_INQUIRY_STATUS,
    statusUpdatedAt: new Date().toISOString(),
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
  return {
    status: DEFAULT_INQUIRY_STATUS,
    statusUpdatedAt: inquiry.createdAt,
    ...inquiry,
  };
}

function createRecommendationFromSupplier(item, index) {
  const distanceKm = Number(item.distanceKm || 6 + index * 2);
  const deliveryCount = Number(item.deliveryCount || 0);
  const priceScore = Math.max(70, 96 - index * 3);
  const distanceScore = Math.max(65, Math.round(100 - distanceKm * 4));
  const reliabilityScore = Math.min(98, 70 + deliveryCount);
  const totalScore = Math.round(priceScore * 0.4 + distanceScore * 0.3 + reliabilityScore * 0.3);

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
    totalScore,
    approvalRequired: item.standard?.includes("ASTM") || item.standard?.includes("JIS"),
    reason: "공급사가 직접 등록한 취급 자재로, 실제 납품 가능 여부는 문의 확인이 필요합니다.",
    contact: item.contact,
    address: item.address,
    serviceArea: item.serviceArea,
    isRegisteredSupplier: true,
  };
}
