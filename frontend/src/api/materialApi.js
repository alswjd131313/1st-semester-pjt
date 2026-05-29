import axios from "axios";
import { latestRequest, nearbySuppliers, rankingMaterials, recommendationResults } from "../data/dummyData";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
  timeout: 5000,
});

export async function getRankingMaterials() {
  // return apiClient.get("/ranking-materials/").then((res) => res.data);
  return Promise.resolve(rankingMaterials);
}

export async function createMaterialRequest(payload) {
  // return apiClient.post("/material-requests/", payload).then((res) => res.data);
  return Promise.resolve({
    ...latestRequest,
    ...payload,
    id: `REQ-${Date.now()}`,
  });
}

export async function getRecommendations(requestId) {
  // return apiClient.get(`/recommendations/${requestId}/`).then((res) => res.data);
  return Promise.resolve({
    request: latestRequest,
    results: recommendationResults,
  });
}

export async function getNearbySuppliers() {
  // return apiClient.get("/nearby-suppliers/").then((res) => res.data);
  return Promise.resolve({
    currentLocation: "서울 성수동 기준",
    totalCount: 12,
    suppliers: nearbySuppliers,
  });
}

export async function registerSupplierMaterial(payload) {
  // return apiClient.post("/supplier-materials/", payload).then((res) => res.data);
  return Promise.resolve({
    id: `SUP-${Date.now()}`,
    ...payload,
  });
}

export { apiClient };
