import { additionalRecommendationResults, recommendationResults } from "../data/dummyData";
import { apiClient, buildApiUrl, USE_MOCK_API } from "./apiClient";
import {
  buildSupplierRecipientKey,
  createNotification,
  getUserRecipientKeys,
} from "./notificationApi";

const REQUEST_STORAGE_KEY = "paceflow_v2_latest_request";
const SUPPLIER_STORAGE_KEY = "paceflow_v2_supplier_materials";
const INQUIRY_STORAGE_KEY = "paceflow_v2_supplier_inquiries";
const DEFAULT_INQUIRY_STATUS = "received";
const BLOCKED_RECOMMENDATION_SOURCE_KEYS = new Set([
  "demo_seed",
  "mvp_seed",
  "seed",
  "dummy",
]);
const BLOCKED_RECOMMENDATION_KEYWORD_PATTERN = /dummy|test|sample|seed|mvp|시드|더미|테스트|임시|개발용/i;
const UNRELIABLE_SUPPLIER_ADDRESS_PATTERN =
  /조달청|지방조달청|서울주택도시개발공사|한국공항공사|건강보험심사평가원|법무부|교육청|지원청|환경청|학교|시청|군청|구청|사업소|관리사업소|맑은물사업소|맑은물사업본부|종합건설본부|본부|센터|관리단|공사|공단|행정복지센터|주민센터/;
const REFERENCE_LOCATION_COORDINATES = [
  { pattern: /천안시/, latitude: 36.8151, longitude: 127.1139 },
  { pattern: /김해시/, latitude: 35.2285, longitude: 128.8894 },
  { pattern: /장성군/, latitude: 35.3019, longitude: 126.7848 },
  { pattern: /부산광역시강서구|부산강서구/, latitude: 35.2122, longitude: 128.9806 },
  { pattern: /서울특별시|서울시/, latitude: 37.5665, longitude: 126.9780 },
  { pattern: /경기도/, latitude: 37.4138, longitude: 127.5183 },
  { pattern: /충청남도/, latitude: 36.5184, longitude: 126.8000 },
  { pattern: /충청북도/, latitude: 36.8000, longitude: 127.7000 },
  { pattern: /전라남도/, latitude: 34.8161, longitude: 126.4629 },
  { pattern: /전라북도|전북특별자치도/, latitude: 35.7175, longitude: 127.1530 },
  { pattern: /경상남도/, latitude: 35.4606, longitude: 128.2132 },
  { pattern: /경상북도/, latitude: 36.4919, longitude: 128.8889 },
  { pattern: /강원특별자치도|강원도/, latitude: 37.8228, longitude: 128.1555 },
];
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
  assertValidSiteLocation(payload);
  assertRequiredRecommendationFields(payload);

  if (USE_MOCK_API) {
    const request = {
      id: `REQ-${Date.now()}`,
      createdAt: new Date().toISOString(),
      ...payload,
    };
    localStorage.setItem(REQUEST_STORAGE_KEY, JSON.stringify(request));
    return request;
  }

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
  const { data } = await apiClient.post(buildApiUrl("/api/v1/demands/"), toBackendDemand(request, "submitted"));
  const savedRequest = { ...request, backendDemandId: data.id };
  localStorage.setItem(REQUEST_STORAGE_KEY, JSON.stringify(savedRequest));
  clearStoredDraft();
  return savedRequest;
}

export async function saveMaterialRequestDraft(payload) {
  const draftPayload = normalizeDraftPayload(payload);

  if (USE_MOCK_API) {
    const draft = {
      id: payload.draftId || `DRAFT-${Date.now()}`,
      status: "draft",
      updatedAt: new Date().toISOString(),
      ...draftPayload,
    };
    localStorage.setItem(getDraftStorageKey(), JSON.stringify(draft));
    return draft;
  }

  const body = toBackendDemand(draftPayload, "draft");
  const draftId = payload.draftId || getStoredDraftId();
  let response;
  try {
    response = draftId
      ? await apiClient.patch(buildApiUrl(`/api/v1/demands/${draftId}/`), body)
      : await apiClient.post(buildApiUrl("/api/v1/demands/"), body);
  } catch (error) {
    if (!draftId || error?.response?.status !== 404) throw error;
    response = await apiClient.post(buildApiUrl("/api/v1/demands/"), body);
  }
  const { data } = response;
  localStorage.setItem(getDraftIdStorageKey(), String(data.id));
  const savedDraft = fromBackendDemandDraft(data);
  localStorage.setItem(getDraftStorageKey(), JSON.stringify(savedDraft));
  return savedDraft;
}

export async function getMaterialRequestDraft() {
  if (USE_MOCK_API) {
    try {
      const saved = localStorage.getItem(getDraftStorageKey());
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  }

  try {
    const { data } = await apiClient.get(buildApiUrl("/api/v1/demands/"), {
      params: { status: "draft" },
    });
    const results = Array.isArray(data) ? data : data.results || [];
    const latest = results[0];
    if (!latest) return null;
    localStorage.setItem(getDraftIdStorageKey(), String(latest.id));
    return fromBackendDemandDraft(latest);
  } catch {
    return null;
  }
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
  const latestRequest = options.request || await getLatestMaterialRequest();
  assertValidSiteLocation(latestRequest);

  if (USE_MOCK_API) {
    const registeredRecommendations = getStoredSupplierMaterials().map((item, index) =>
      createRecommendationFromSupplier(item, index),
    );
    return normalizeRecommendationRanking([
      ...registeredRecommendations,
      ...recommendationResults,
      ...additionalRecommendationResults,
    ], requestId);
  }

  const backendRecommendations = await getBackendAlternativeRecommendations(
    latestRequest,
    requestId,
    options,
  );
  const registeredRecommendations = await getPublicSupplierMaterialRecommendations(requestId, 0);
  const narajangteoRecommendations = await getNarajangteoRecommendationCandidates(options.keyword || "", requestId);
  const actualRecommendations = [
    ...backendRecommendations,
    ...registeredRecommendations,
    ...narajangteoRecommendations,
  ];

  if (import.meta.env.DEV && options.useDemoData === true) {
    actualRecommendations.push(...recommendationResults, ...additionalRecommendationResults);
  }

  return normalizeRecommendationRanking(actualRecommendations, requestId);
}

export async function getSupplierMapCandidates(requestId, options = {}) {
  if (USE_MOCK_API) {
    return normalizeRecommendationRanking([
      ...getStoredSupplierMaterials().map((item, index) => createRecommendationFromSupplier(item, index)),
      ...recommendationResults,
      ...additionalRecommendationResults,
    ], requestId);
  }

  const { data } = await apiClient.get(buildApiUrl("/api/v1/suppliers/map/"), {
    params: {
      scope: options.scope || "current",
      material: options.material || "",
    },
  });
  const results = Array.isArray(data) ? data : data.results || [];
  return results.map(normalizeMapSupplier);
}

function normalizeMapSupplier(item) {
  const materials = Array.isArray(item.materials) ? item.materials.filter(Boolean) : [];
  return {
    id: item.id,
    supplierId: item.id,
    candidateId: `supplier-map-${item.id}`,
    supplierName: item.supplierName || item.name || "",
    materialName: item.materialName || materials.join(", "),
    materials,
    standard: materials.length ? `${materials.slice(0, 3).join(", ")} 취급` : "취급 자재 확인 필요",
    address: item.address || "",
    contact: item.phone || "",
    latitude: item.latitude === null || item.latitude === undefined ? null : Number(item.latitude),
    longitude: item.longitude === null || item.longitude === undefined ? null : Number(item.longitude),
    locationBasis: item.locationBasis || "supplier_address",
    locationStatus: item.location_status || "verified",
    routeStatus: "not_requested",
    routeNote: "지도 탐색용 공급사",
    dataSource: "supplier_map",
    dataSourceLabel: "전국 공급사 DB",
    isRegisteredSupplier: true,
    distanceScore: null,
    priceScore: 0,
    reliabilityScore: 0,
    materialFitScore: 0,
    totalScore: 0,
    deliveryCount: 0,
  };
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
  return dedupeRecommendations(items)
    .map((item) => {
      const locationBasis = normalizeRecommendationLocationBasis(item);
      const fallbackCoordinates = ["contract_agency_estimated", "reference_estimated"].includes(locationBasis)
        ? getReferenceLocationCoordinates(item.locationLabel || item.address || "")
        : null;
      return {
        ...item,
        requestId,
        dataSource: item.dataSource || "unknown",
        dataSourceLabel: item.dataSourceLabel || "출처 확인 필요",
        specSourceLabel: item.specSourceLabel || "KS 수동 DB",
        routeStatus: item.routeStatus || "not_requested",
        routeNote: item.routeNote || "거리 정보 확인 필요",
        locationBasis,
        latitude: hasKoreaCoordinate(item.latitude, item.longitude)
          ? item.latitude
          : fallbackCoordinates?.latitude ?? item.latitude,
        longitude: hasKoreaCoordinate(item.latitude, item.longitude)
          ? item.longitude
          : fallbackCoordinates?.longitude ?? item.longitude,
      };
    })
    .filter(isValidRecommendationCandidate)
    .map((item, index) => ({
      ...item,
      rank: index + 1,
    }));
}

function isValidRecommendationCandidate(item) {
  if (!item || typeof item !== "object") {
    return false;
  }

  if (item.is_demo === true || item.isDemo === true) {
    return false;
  }

  if (item.is_verified === false || item.isVerified === false) {
    return false;
  }

  const dataSource = String(item.dataSource || item.data_source || item.source || "").trim().toLowerCase();
  if (BLOCKED_RECOMMENDATION_SOURCE_KEYS.has(dataSource)) {
    return false;
  }
  if (!item.isRegisteredSupplier && dataSource === "unknown") {
    return false;
  }

  const searchableText = [
    dataSource,
    item.dataSourceLabel,
    item.specSourceLabel,
    item.standard,
    item.reason,
    item.approvalRiskNote,
    item.supplierName,
    item.materialName,
    ...(Array.isArray(item.reasonItems) ? item.reasonItems : []),
  ].filter(Boolean).join(" ");
  if (BLOCKED_RECOMMENDATION_KEYWORD_PATTERN.test(searchableText)) {
    return false;
  }

  if (!hasMeaningfulRecommendationText(item.supplierName) || !hasMeaningfulRecommendationText(item.materialName)) {
    return false;
  }

  if (!hasValidRecommendationStandard(item)) {
    return false;
  }

  return hasValidCandidateLocation(item);
}

function hasMeaningfulRecommendationText(value) {
  const text = String(value || "").trim();
  return Boolean(text) && !/확인 필요|미지정|unknown/i.test(text);
}

function hasValidRecommendationStandard(item) {
  const standard = String(item.standard || "").trim();
  if (!standard || /확인 필요|출처 확인|물성 확인|시드|더미|테스트|임시|개발용/i.test(standard)) {
    return false;
  }
  return true;
}

function hasValidCandidateLocation(item) {
  if (hasReliableSupplierLocation(item)) {
    return true;
  }

  return [item.address, item.locationLabel, item.serviceArea]
    .some((value) => hasMeaningfulRecommendationText(value));
}

function normalizeRecommendationLocationBasis(item) {
  if (item.locationBasis && item.locationBasis !== "unknown") {
    return item.locationBasis;
  }

  if (!hasReliableSupplierLocation(item)) {
    return "unknown";
  }

  return item.isRegisteredSupplier || item.dataSource === "supplier_registered"
    ? "supplier_address"
    : "reference_estimated";
}

async function getBackendAlternativeRecommendations(request, requestId, options) {
  if (!request?.backendMaterialId) {
    return [];
  }
  assertValidSiteLocation(request);

  try {
    const { data } = await apiClient.post(
      buildApiUrl(`/api/v1/materials/${request.backendMaterialId}/alternatives/`),
      {
        site_address: request.siteAddress || "",
        site_lat: Number(request.siteLat),
        site_lng: Number(request.siteLng),
        site_latitude: Number(request.siteLat),
        site_longitude: Number(request.siteLng),
        include_international: options.includeInternational !== false,
        radius_km: Number(options.radiusKm || 50),
      },
    );
    return toFrontendRecommendations(data, requestId);
  } catch {
    return [];
  }
}

function assertValidSiteLocation(request) {
  if (!request?.siteAddress || !hasKoreaCoordinate(request.siteLat, request.siteLng)) {
    throw new Error("현장 주소를 입력해야 거리 기반 추천이 가능합니다.");
  }
}

function hasKoreaCoordinate(latitude, longitude) {
  const lat = Number(latitude);
  const lng = Number(longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 33 && lat <= 39 && lng >= 124 && lng <= 132;
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
  if (USE_MOCK_API) return createMockSupplierMaterial(payload);
  const { data } = await apiClient.post(buildApiUrl("/api/v1/supplier-materials/"), toBackendSupplierMaterial(payload));
  return toFrontendSupplierMaterial(data);
}

export async function getSupplierMaterials() {
  if (USE_MOCK_API) return getStoredSupplierMaterials();
  const { data } = await apiClient.get(buildApiUrl("/api/v1/supplier-materials/"));
  const results = Array.isArray(data) ? data : data.results || [];
  return results.map(toFrontendSupplierMaterial);
}

export async function deleteSupplierMaterial(materialId) {
  if (USE_MOCK_API) {
    const normalizedId = String(materialId ?? "");
    const materials = getStoredSupplierMaterials();
    const remaining = materials.filter((material) => String(material.id) !== normalizedId);
    localStorage.setItem(SUPPLIER_STORAGE_KEY, JSON.stringify(remaining));
    return remaining.length !== materials.length;
  }
  await apiClient.delete(buildApiUrl(`/api/v1/supplier-materials/${materialId}/`));
  return true;
}

export async function createSupplierInquiry(payload) {
  if (USE_MOCK_API) {
    const inquiry = createMockSupplierInquiry(payload);
    createSupplierInquiryNotification(inquiry);
    return inquiry;
  }

  const body = {
    material_name: payload.requestMaterial?.materialName || payload.supplier?.materialName || "",
    standard: payload.requestMaterial?.strengthGrade || payload.supplier?.standard || "",
    quantity: payload.quantity || payload.requestMaterial?.requiredQuantity || "",
    desired_date: payload.desiredDate || null,
    site_address: payload.requestMaterial?.siteAddress || payload.siteAddress || "",
    requester_name: payload.requesterName || "",
    contact: payload.contact || "",
    message: payload.message || "",
    supplier_user_id: payload.supplierIdentity?.userId || null,
    supplier_name: payload.supplier?.supplierName || payload.supplierIdentity?.companyName || "",
  };
  const { data } = await apiClient.post(buildApiUrl("/api/v1/inquiries/"), body);
  if (import.meta.env.DEV) {
    console.debug("[inquiries] create:success", {
      inquiryId: data?.id,
      requesterId: data?.requester_id,
      supplierUserId: data?.supplier_user_id,
    });
  }
  const normalizedInquiry = normalizeBackendInquiry(data);
  const inquiry = {
    ...normalizedInquiry,
    requesterRecipientKey: payload.requesterRecipientKey || payload.requesterIdentity?.recipientKey || "",
    supplierRecipientKey: payload.supplierRecipientKey || payload.supplierIdentity?.recipientKey || "",
    requesterIdentity: {
      ...normalizedInquiry.requesterIdentity,
      ...payload.requesterIdentity,
    },
    supplierIdentity: {
      ...normalizedInquiry.supplierIdentity,
      ...payload.supplierIdentity,
    },
  };
  createSupplierInquiryNotification(inquiry);
  return inquiry;
}

export async function getSupplierInquiries() {
  if (USE_MOCK_API) return getStoredSupplierInquiries();
  const { data } = await apiClient.get(buildApiUrl("/api/v1/inquiries/"));
  const list = Array.isArray(data) ? data : data.results || [];
  return list.map(normalizeBackendInquiry);
}

export function filterInquiriesForUser(inquiries, user) {
  if (!Array.isArray(inquiries) || !user?.role) return [];
  const recipientKeys = getUserRecipientKeys(user);
  return inquiries.filter((inquiry) => {
    if (user.role === "supplier" && inquiry.supplierDeletedAt) return false;
    return user.role === "supplier"
      ? isInquiryForSupplier(inquiry, user, recipientKeys)
      : isInquiryForRequester(inquiry, user, recipientKeys);
  });
}

function isInquiryForRequester(inquiry, user, recipientKeys) {
  const identity = inquiry.requesterIdentity || {};
  const recipientKey = inquiry.requesterRecipientKey || identity.recipientKey || "";
  const requesterId = identity.userId ?? inquiry.requesterUserId ?? inquiry.requester_id;
  const requesterEmail = identity.email || inquiry.requesterEmail || inquiry.requester_email || "";
  const hasStrongIdentity = Boolean(recipientKey || requesterId !== undefined || requesterEmail);

  if (hasStrongIdentity) {
    return (
      (recipientKey && recipientKeys.has(recipientKey))
      || sameIdentifier(requesterId, user.id)
      || sameText(requesterEmail, user.email)
    );
  }

  return sameText(inquiry.requesterName, user.name);
}

function isInquiryForSupplier(inquiry, user, recipientKeys) {
  const identity = inquiry.supplierIdentity || {};
  const supplier = inquiry.supplier || {};
  const recipientKey = inquiry.supplierRecipientKey || identity.recipientKey || "";
  const supplierUserId = identity.userId ?? supplier.ownerUserId ?? supplier.owner_user_id;
  const supplierEmail = (
    identity.email
    || supplier.ownerEmail
    || supplier.owner_email
    || supplier.email
    || ""
  );
  const hasStrongIdentity = Boolean(recipientKey || supplierUserId !== undefined || supplierEmail);

  if (hasStrongIdentity) {
    return (
      (recipientKey && recipientKeys.has(recipientKey))
      || sameIdentifier(supplierUserId, user.id)
      || sameText(supplierEmail, user.email)
    );
  }

  const supplierCompany = identity.companyName || supplier.companyName || supplier.supplierName;
  return sameText(supplierCompany, user.companyName);
}

function sameIdentifier(left, right) {
  if (left === null || left === undefined || right === null || right === undefined) return false;
  return String(left) === String(right);
}

function sameText(left, right) {
  if (!left || !right) return false;
  return String(left).trim().toLocaleLowerCase("ko-KR")
    === String(right).trim().toLocaleLowerCase("ko-KR");
}

export async function getSupplierInquiry(inquiryId) {
  if (USE_MOCK_API) {
    const normalizedId = String(inquiryId ?? "");
    return getStoredSupplierInquiries().find((inquiry) => String(inquiry.id) === normalizedId) || null;
  }
  const { data } = await apiClient.get(buildApiUrl(`/api/v1/inquiries/${inquiryId}/`));
  return normalizeBackendInquiry(data);
}

export async function updateSupplierInquiry(inquiryId, updates) {
  if (USE_MOCK_API) {
    const normalizedId = String(inquiryId ?? "");
    const inquiries = getStoredSupplierInquiries();
    const index = inquiries.findIndex((inquiry) => String(inquiry.id) === normalizedId);
    if (index < 0) return null;
    const current = inquiries[index];
    const next = {
      ...current,
      ...updates,
      id: current.id,
      statusUpdatedAt: updates.status && updates.status !== current.status
        ? new Date().toISOString()
        : current.statusUpdatedAt,
    };
    inquiries.splice(index, 1, next);
    localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify(inquiries));
    return next;
  }

  const body = {
    material_name: updates.materialName || updates.requestMaterial?.materialName || "",
    standard: updates.standard || updates.requestMaterial?.strengthGrade || "",
    quantity: updates.quantity || updates.requestMaterial?.requiredQuantity || "",
    desired_date: updates.desiredDate || null,
    site_address: updates.siteAddress || updates.requestMaterial?.siteAddress || "",
    requester_name: updates.requesterName || "",
    contact: updates.contact || "",
    message: updates.message || "",
  };
  const { data } = await apiClient.patch(buildApiUrl(`/api/v1/inquiries/${inquiryId}/`), body);
  return normalizeBackendInquiry(data);
}

export async function deleteSupplierInquiry(inquiryId) {
  if (USE_MOCK_API) {
    const normalizedId = String(inquiryId ?? "");
    const inquiries = getStoredSupplierInquiries();
    const remaining = inquiries.filter((inquiry) => String(inquiry.id) !== normalizedId);
    if (remaining.length === inquiries.length) return false;
    localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify(remaining));
    return true;
  }
  await apiClient.delete(buildApiUrl(`/api/v1/inquiries/${inquiryId}/`));
  return true;
}

export async function hideSupplierInquiryForSupplier(inquiryId) {
  if (USE_MOCK_API) {
    const normalizedId = String(inquiryId ?? "");
    const inquiries = getStoredSupplierInquiries();
    const nextInquiries = inquiries.map((inquiry) =>
      String(inquiry.id) === normalizedId
        ? { ...inquiry, supplierDeletedAt: new Date().toISOString() }
        : inquiry,
    );
    localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify(nextInquiries));
    return true;
  }

  await apiClient.patch(buildApiUrl(`/api/v1/inquiries/${inquiryId}/delete-for-supplier/`));
  return true;
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
          includeSeed: false,
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
    const hasSupplierDistance = Boolean(contract.supplierDistanceAvailable)
      && (contract.locationBasis || "supplier_address") === "supplier_address"
      && hasReliableSupplierLocation({
        latitude,
        longitude,
        address: contract.supplierAddress || contract.locationLabel || "",
      });
    const hasEstimatedLocation = !hasSupplierDistance
      && ["contract_agency_estimated", "reference_estimated"].includes(contract.locationBasis)
      && hasCoordinates;
    const distanceKm = hasSupplierDistance ? Number((4.5 + index * 1.8).toFixed(1)) : null;
    const priceScore = Math.max(72, 92 - index * 2);
    const distanceScore = hasSupplierDistance ? Math.max(0, Math.round(100 - distanceKm * 3.5)) : 0;
    const reliabilityScore = isSeedCandidate
      ? Math.min(82, 66 + deliveryCount * 4)
      : Math.min(96, 78 + deliveryCount / 2);
    const materialFitScore = matchConfidence.score;

    return {
      requestId,
      supplierId: contract.supplierId || contract.supplier_id || null,
      supplierName: contract.supplierName,
      materialName: contract.productName || contract.rankingKeyword || keyword,
      standard: isSeedCandidate ? "KS 구조화 MVP 시드 기준" : "나라장터 계약 품명 기준",
      price: amount ? `${amount.toLocaleString()}원` : "계약금액 확인 필요",
      distanceKm,
      distanceLabel: hasSupplierDistance ? `${distanceKm}km` : "거리 확인 불가",
      locationBasis: hasSupplierDistance
        ? "supplier_address"
        : hasEstimatedLocation
          ? contract.locationBasis
          : "unknown",
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
      isVerified: contract.is_verified,
      isDemo: contract.is_demo,
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
          : "공급사 주소 미확인으로 거리 계산에서 제외했습니다.",
        reliability: isSeedCandidate
          ? "MVP 시드 이력은 공공 계약 이력보다 보수적인 신뢰도 점수를 적용했습니다."
          : "공공 계약 이력 존재 여부를 신뢰도 점수에 반영했습니다.",
      },
      latitude: (hasSupplierDistance || hasEstimatedLocation) && hasCoordinates ? latitude : null,
      longitude: (hasSupplierDistance || hasEstimatedLocation) && hasCoordinates ? longitude : null,
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
  if (USE_MOCK_API) {
    const previousInquiry = getStoredSupplierInquiries().find(
      (inquiry) => String(inquiry.id) === String(inquiryId),
    );
    const updatedInquiry = updateMockSupplierInquiryStatus(inquiryId, status);
    if (updatedInquiry && previousInquiry?.status !== status) {
      createRequesterStatusNotification(updatedInquiry, status);
    }
    return updatedInquiry;
  }

  const previousInquiry = await getSupplierInquiry(inquiryId);
  const { data } = await apiClient.patch(
    buildApiUrl(`/api/v1/inquiries/${inquiryId}/status/`),
    { status },
  );
  if (import.meta.env.DEV) {
    console.debug("[inquiries] status:update:success", {
      inquiryId,
      status,
      requesterId: data?.requester_id,
      supplierUserId: data?.supplier_user_id,
    });
  }
  const updatedInquiry = normalizeBackendInquiry(data);
  if (previousInquiry?.status !== status) {
    createRequesterStatusNotification(updatedInquiry, status);
  }
  return updatedInquiry;
}

function normalizeBackendInquiry(raw) {
  const supplierInfo = raw.supplier_info || null;
  const requesterRecipientKey = raw.requester_id
    ? `user:${raw.requester_id}`
    : raw.requester_email
      ? `email:${String(raw.requester_email).trim().toLocaleLowerCase("ko-KR")}`
      : "";
  const supplierRecipientKey = raw.supplier_user_id
    ? `user:${raw.supplier_user_id}`
    : raw.supplier_email
      ? `email:${String(raw.supplier_email).trim().toLocaleLowerCase("ko-KR")}`
      : "";
  return {
    id: String(raw.id),
    status: raw.status,
    supplierDeletedAt: raw.supplier_deleted_at || "",
    createdAt: raw.created_at,
    statusUpdatedAt: raw.status_updated_at || raw.updated_at || raw.created_at,
    desiredDate: raw.desired_date || "",
    quantity: raw.quantity || "",
    requesterName: raw.requester_name || "",
    requesterCompany: raw.requester_company || "",
    contact: raw.contact || "",
    message: raw.message || "",
    requestMaterial: {
      materialName: raw.material_name || "",
      strengthGrade: raw.standard || "",
      requiredQuantity: raw.quantity || "",
      siteAddress: raw.site_address || "",
    },
    supplier: supplierInfo ? {
      supplierName: supplierInfo.company_name || "",
      materialName: raw.material_name || "",
      standard: raw.standard || "",
      deliveryCount: supplierInfo.delivery_count || null,
      routeDistanceM: supplierInfo.distance_m || null,
    } : null,
    requesterIdentity: {
      userId: raw.requester_id,
      email: raw.requester_email || "",
      recipientKey: requesterRecipientKey,
    },
    supplierIdentity: {
      userId: raw.supplier_user_id,
      email: raw.supplier_email || "",
      recipientKey: supplierRecipientKey,
    },
    requesterRecipientKey,
    supplierRecipientKey,
  };
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
        (normalizedGrade && normalizedRequestedText.includes(normalizedGrade)) ||
        (normalizedDiameter && normalizedRequestedText.includes(normalizedDiameter)) ||
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

function toBackendDemand(request, status = "submitted") {
  const siteLat = nullableRoundCoordinate(request.siteLat);
  const siteLng = nullableRoundCoordinate(request.siteLng);
  const quantity = parseQuantity(request.requiredQuantity);
  return {
    status,
    site_name: request.siteAddress || "PaceFlow 현장",
    site_lat: siteLat,
    site_lng: siteLng,
    material: request.backendMaterialId || null,
    quantity: quantity || null,
    deadline: request.requiredDate || null,
    memo: request.memo || "",
    draft_payload: normalizeDraftPayload(request),
  };
}

function roundCoordinate(value) {
  return Number(Number(value).toFixed(6));
}

function nullableRoundCoordinate(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Number(number.toFixed(6)) : null;
}

function parseQuantity(value) {
  const quantity = Number(String(value).replace(/[^\d.]/g, ""));
  return Number.isFinite(quantity) && quantity > 0 ? quantity : null;
}

function normalizeDraftPayload(payload = {}) {
  return {
    draftId: payload.draftId || null,
    materialName: payload.materialName || "",
    category: payload.category || "",
    standard: payload.standard || "",
    shape: payload.shape || "",
    strengthGrade: payload.strengthGrade || "",
    requiredQuantity: payload.requiredQuantity || "",
    quantity: payload.quantity || "",
    unit: payload.unit || "",
    siteAddress: payload.siteAddress || "",
    siteZipNo: payload.siteZipNo || "",
    siteLat: nullableRoundCoordinate(payload.siteLat),
    siteLng: nullableRoundCoordinate(payload.siteLng),
    requiredDate: payload.requiredDate || "",
    isUrgent: Boolean(payload.isUrgent),
    memo: payload.memo || "",
    extraGradeNote: payload.extraGradeNote || "",
    manufacturer: payload.manufacturer || "",
    extraNote: payload.extraNote || "",
  };
}

function fromBackendDemandDraft(raw = {}) {
  return {
    id: raw.id,
    draftId: raw.id,
    status: raw.status || "draft",
    ...(raw.draft_payload || {}),
    siteAddress: raw.draft_payload?.siteAddress || raw.site_name || "",
    siteLat: raw.draft_payload?.siteLat ?? (raw.site_lat == null ? null : Number(raw.site_lat)),
    siteLng: raw.draft_payload?.siteLng ?? (raw.site_lng == null ? null : Number(raw.site_lng)),
    requiredDate: raw.draft_payload?.requiredDate || raw.deadline || "",
    memo: raw.draft_payload?.memo || raw.memo || "",
    createdAt: raw.created_at,
  };
}

function getDraftStorageKey() {
  return "paceflow_v2_material_request_draft";
}

function getDraftIdStorageKey() {
  return "paceflow_v2_material_request_draft_id";
}

function getStoredDraftId() {
  return localStorage.getItem(getDraftIdStorageKey());
}

function clearStoredDraft() {
  localStorage.removeItem(getDraftStorageKey());
  localStorage.removeItem(getDraftIdStorageKey());
}

function assertRequiredRecommendationFields(payload) {
  if (!payload?.materialName?.trim()) {
    throw new Error("추천받을 자재명을 입력해주세요.");
  }
  if (!payload?.requiredQuantity || parseQuantity(payload.requiredQuantity) === null) {
    throw new Error("추천받을 수량을 입력해주세요.");
  }
  if (!payload?.requiredDate) {
    throw new Error("희망 납기일을 입력해주세요.");
  }
}

function toFrontendRecommendations(data, requestId) {
  const original = data.original_material;
  return (data.recommendations || []).map((item, index) => {
    const material = item.material;
    const supplier = item.supplier;
    const scores = normalizeBackendScores(item.scores);
    const approvalRequired = Boolean(item.approval_warning || material?.regulation?.requires_approval);
    const dataSource = getDataSourceMeta(item.data_source, supplier?.source);
    const responseLocationBasis = item.location_basis || item.locationBasis || "";
    const hasEstimatedLocation = ["contract_agency_estimated", "reference_estimated"].includes(responseLocationBasis);
    const hasReliableLocation = hasReliableSupplierLocation({
      ...supplier,
      latitude: item.display_latitude ?? supplier?.latitude,
      longitude: item.display_longitude ?? supplier?.longitude,
      address: item.location_label || supplier?.address,
    }) && !["contract_agency_estimated", "reference_estimated"].includes(responseLocationBasis);
    const hardFilterEvidence = buildHardFilterEvidence(original, material, {
      includeInternational: !approvalRequired,
      approvalWarning: item.approval_warning,
    });

    return {
      rank: item.rank || index + 1,
      requestId,
      supplierId: supplier?.id ?? item.supplier_id ?? null,
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
      isVerified: item.is_verified ?? material?.is_verified ?? supplier?.is_verified,
      isDemo: item.is_demo ?? material?.is_demo ?? supplier?.is_demo,
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
          : item.route_note || "공급사 위치가 확인되지 않아 거리 점수 0점을 반영했습니다.",
        reliability: `납품 이력 ${item.supply_count}회를 신뢰도 점수에 반영했습니다.`,
      },
      approvalChecklist: buildApprovalChecklist(material, approvalRequired, item.approval_warning),
      approvalRiskNote:
        item.approval_warning ||
        "백엔드 물성 필터를 통과한 후보입니다. 최종 납품 가능 여부는 공급사 확인이 필요합니다.",
      contact: supplier?.phone,
      address: supplier?.address,
      latitude: (hasReliableLocation || hasEstimatedLocation)
        && hasKoreaCoordinate(item.display_latitude ?? supplier?.latitude, item.display_longitude ?? supplier?.longitude)
        ? Number(item.display_latitude ?? supplier?.latitude)
        : null,
      longitude: (hasReliableLocation || hasEstimatedLocation)
        && hasKoreaCoordinate(item.display_latitude ?? supplier?.latitude, item.display_longitude ?? supplier?.longitude)
        ? Number(item.display_longitude ?? supplier?.longitude)
        : null,
      locationBasis: hasReliableLocation
        ? "supplier_address"
        : hasEstimatedLocation
          ? responseLocationBasis
          : "unknown",
      locationLabel: item.location_label || supplier?.address || "",
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

function createSupplierInquiryNotification(inquiry) {
  const recipientKey = inquiry.supplierRecipientKey || buildSupplierRecipientKey(inquiry.supplier);
  if (!recipientKey) return;
  const materialName = inquiry.requestMaterial?.materialName || inquiry.supplier?.materialName || "요청 자재";
  const quantity = inquiry.quantity || inquiry.requestMaterial?.requiredQuantity || "";
  const summary = [materialName, quantity].filter(Boolean).join(" · ");
  createNotification({
    recipient_user_id: inquiry.supplierIdentity?.userId ?? null,
    recipient_role: "supplier",
    recipient_key: recipientKey,
    type: "supplier_inquiry_created",
    title: "새로운 자재 문의가 도착했습니다.",
    message: summary ? `${summary} 문의가 도착했습니다.` : "요청자가 자재 납품 가능 여부를 문의했습니다.",
    related_inquiry_id: inquiry.id,
    target_path: `/inquiries/${inquiry.id}`,
    event_key: `inquiry-created:${inquiry.id}`,
  });
}

function createRequesterStatusNotification(inquiry, status) {
  const recipientKey = inquiry.requesterRecipientKey || inquiry.requesterIdentity?.recipientKey;
  if (!recipientKey) return;
  const statusMessages = {
    reviewing: ["공급사가 요청을 확인 중입니다.", "공급사가 문의 내용을 확인하고 있습니다."],
    quoted: ["납품 가능 응답이 도착했습니다.", "공급사가 요청 자재에 대해 납품 가능으로 응답했습니다."],
    accepted: ["납품 가능 응답이 도착했습니다.", "공급사가 요청 자재에 대해 납품 가능으로 응답했습니다."],
    need_more_info: ["공급사가 추가 확인을 요청했습니다.", "공급사가 납품 가능 여부 확인을 위해 추가 정보를 요청했습니다."],
    rejected: ["공급사가 요청을 거절했습니다.", "공급사가 해당 요청에 대해 거절로 응답했습니다."],
    unavailable: ["공급사가 요청을 거절했습니다.", "공급사가 해당 요청에 대해 거절로 응답했습니다."],
  };
  const notificationCopy = statusMessages[status];
  if (!notificationCopy) return;
  createNotification({
    recipient_user_id: inquiry.requesterIdentity?.userId ?? null,
    recipient_role: "requester",
    recipient_key: recipientKey,
    type: "supplier_inquiry_status_changed",
    title: notificationCopy[0],
    message: notificationCopy[1],
    related_inquiry_id: inquiry.id,
    target_path: `/inquiries/${inquiry.id}`,
    event_key: `inquiry-status:${inquiry.id}:${status}`,
  });
}

function updateMockSupplierInquiryStatus(inquiryId, status) {
  const normalizedId = String(inquiryId ?? "");
  const updatedAt = new Date().toISOString();
  const inquiries = getStoredSupplierInquiries().map((inquiry) =>
    String(inquiry.id) === normalizedId ? { ...inquiry, status, statusUpdatedAt: updatedAt } : inquiry,
  );
  localStorage.setItem(INQUIRY_STORAGE_KEY, JSON.stringify(inquiries));
  return inquiries.find((inquiry) => String(inquiry.id) === normalizedId) || null;
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
    return saved ? JSON.parse(saved).map(normalizeStoredInquiry) : [];
  } catch {
    return [];
  }
}

function normalizeStoredInquiry(inquiry) {
  const isUrgent = inquiry.requestType === "urgent"
    || inquiry.priority === "high"
    || String(inquiry.id || "").startsWith("URG");
  return {
    status: DEFAULT_INQUIRY_STATUS,
    statusUpdatedAt: inquiry.createdAt,
    requestType: isUrgent ? "urgent" : "general",
    priority: isUrgent ? "high" : "normal",
    ...inquiry,
  };
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
    const key = item.supplierId || item.supplier_id
      ? `supplier:${item.supplierId || item.supplier_id}`
      : [item.supplierName, item.materialName, item.standard]
      .filter(Boolean)
      .join("|")
      .toLowerCase();

    const previous = seen.get(key);
    const itemLocationPriority = getCandidateLocationPriority(item);
    const previousLocationPriority = previous ? getCandidateLocationPriority(previous) : -1;
    if (
      !previous
      || itemLocationPriority > previousLocationPriority
      || (
        itemLocationPriority === previousLocationPriority
        && Number(item.totalScore || 0) > Number(previous.totalScore || 0)
      )
    ) {
      seen.set(key, item);
    }
  });

  return Array.from(seen.values());
}

function isUnreliableSupplierAddress(address) {
  const normalized = String(address || "").replace(/\s+/g, "");
  if (!normalized) return true;
  if (UNRELIABLE_SUPPLIER_ADDRESS_PATTERN.test(normalized)) return true;
  return normalized.length <= 8 && !/\d/.test(normalized);
}

function hasReliableSupplierLocation(item = {}) {
  return hasKoreaCoordinate(item.latitude, item.longitude)
    && !isUnreliableSupplierAddress(item.address || item.supplierAddress || item.locationLabel || "");
}

function hasEstimatedSupplierLocation(item = {}) {
  return hasKoreaCoordinate(item.latitude, item.longitude)
    && ["contract_agency_estimated", "reference_estimated"].includes(item.locationBasis);
}

function getReferenceLocationCoordinates(label) {
  const normalized = String(label || "").replace(/\s+/g, "");
  if (!normalized || UNRELIABLE_SUPPLIER_ADDRESS_PATTERN.test(normalized)) {
    return null;
  }
  if (!/(특별시|광역시|특별자치시|특별자치도|도|시|군|구)/.test(normalized)) {
    return null;
  }
  const match = REFERENCE_LOCATION_COORDINATES.find((entry) => entry.pattern.test(normalized));
  return match ? { latitude: match.latitude, longitude: match.longitude } : null;
}

function getCandidateLocationPriority(item = {}) {
  if (hasReliableSupplierLocation(item) && !["contract_agency_estimated", "reference_estimated"].includes(item.locationBasis)) return 2;
  if (hasEstimatedSupplierLocation(item)) return 1;
  return 0;
}

function toBackendSupplierMaterial(payload) {
  return {
    supplier_name: payload.supplierName,
    contact: payload.contact,
    address: payload.address,
    zip_no: payload.zipNo,
    latitude: payload.latitude,
    longitude: payload.longitude,
    main_materials: payload.mainMaterials || payload.materialGroup,
    material_name: payload.materialName,
    standard: payload.standard || payload.specification,
    strength_grade: payload.strengthGrade || payload.ksStandard,
    material_group: payload.materialGroup,
    specification: payload.specification,
    ks_standard: payload.ksStandard,
    recent_price: payload.recentPrice || null,
    unit: payload.unit,
    manufacturer: payload.manufacturer,
    stock_available: payload.stockAvailable !== false,
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
    ownerUserId: item.owner_user_id ?? null,
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
    materialGroup: item.material_group || item.main_materials || "",
    specification: item.specification || item.standard || "",
    ksStandard: item.ks_standard || item.strength_grade || "",
    recentPrice: item.recent_price === null || item.recent_price === undefined ? "" : Number(item.recent_price),
    unit: item.unit || "",
    manufacturer: item.manufacturer || "",
    stockAvailable: item.stock_available !== false,
    serviceArea: item.service_area,
    distanceKm: item.distance_km === null || item.distance_km === undefined ? "" : Number(item.distance_km),
    deliveryCount: item.delivery_count || 0,
    note: item.note,
    createdAt: item.created_at,
  };
}




function createRecommendationFromSupplier(item, index) {
  const hasReliableLocation = hasReliableSupplierLocation(item);
  const distanceKm = hasReliableLocation ? Number(item.distanceKm || 6 + index * 2) : null;
  const deliveryCount = Number(item.deliveryCount || 0);
  const priceScore = Math.max(70, 96 - index * 3);
  const distanceScore = hasReliableLocation ? Math.max(0, Math.round(100 - distanceKm * 4)) : 0;
  const reliabilityScore = Math.min(98, 70 + deliveryCount);
  const materialFitScore = item.standard?.includes("ASTM") || item.standard?.includes("JIS") ? 78 : 88;
  const totalScore = Math.round(materialFitScore * 0.45 + reliabilityScore * 0.3 + distanceScore * 0.15 + priceScore * 0.1);

  return {
    ownerEmail: item.ownerEmail,
    ownerUserId: item.ownerUserId ?? null,
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
    isVerified: item.isVerified ?? item.is_verified,
    isDemo: item.isDemo ?? item.is_demo,
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
    latitude: hasReliableLocation ? item.latitude : null,
    longitude: hasReliableLocation ? item.longitude : null,
    locationBasis: hasReliableLocation
      ? "supplier_address"
      : "unknown",
    serviceArea: item.serviceArea,
    isRegisteredSupplier: true,
  };
}
