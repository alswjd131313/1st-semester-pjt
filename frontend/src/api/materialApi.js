import { recommendationResults } from "../data/dummyData";

const REQUEST_STORAGE_KEY = "paceflow_v2_latest_request";

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
  return recommendationResults.map((item) => ({
    ...item,
    requestId,
  }));
}

export async function registerSupplierMaterial(payload) {
  return {
    id: "SUP-MOCK-001",
    ...payload,
  };
}
