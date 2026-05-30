import { recommendationResults } from "../data/dummyData";

const REQUEST_STORAGE_KEY = "paceflow_v2_latest_request";
const SUPPLIER_STORAGE_KEY = "paceflow_v2_supplier_materials";
const INQUIRY_STORAGE_KEY = "paceflow_v2_supplier_inquiries";
const DEFAULT_INQUIRY_STATUS = "received";

export async function createMaterialRequest(payload) {
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
  const material = {
    id: `SUP-${Date.now()}`,
    createdAt: new Date().toISOString(),
    ...payload,
  };

  const savedMaterials = getStoredSupplierMaterials();
  localStorage.setItem(SUPPLIER_STORAGE_KEY, JSON.stringify([material, ...savedMaterials]));
  return material;
}

export async function getSupplierMaterials() {
  return getStoredSupplierMaterials();
}

export async function createSupplierInquiry(payload) {
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

export async function getSupplierInquiries() {
  return getStoredSupplierInquiries();
}

export async function updateSupplierInquiryStatus(inquiryId, status) {
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
